from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.core.cache import cache
from django.db.models import QuerySet

from apps.posts.constants import CATEGORY_L2_LABELS
from apps.posts.filters import apply_post_hard_filters, apply_post_search_query
from apps.posts.models import Post, PostAttribute

from . import constants
from .models import ImageEmbedding, MatchCandidate
from .providers import get_provider
from .vectors import cosine_score, source_hash


@dataclass
class QueryContext:
    searcher_id: int
    source_post: Post | None
    target_type: str
    category_l1: str | None
    region_code: str | None
    place_id: int | None
    event_start: datetime | None
    event_end: datetime | None
    q: str
    query_vectors: list[list[float]]
    query_l2: str | None
    query_place_id: int | None
    query_brand: str
    query_color: str
    adhoc_text: str


@dataclass
class RankedHit:
    post: Post
    score: float
    vector_score: float
    reason: str
    keyword_hit: bool
    match: MatchCandidate | None = None


def opposite_type(post_type: str) -> str:
    if post_type == "lost":
        return "found"
    if post_type == "found":
        return "lost"
    raise ValueError("type 必须是 lost 或 found")


def default_time_window(post: Post) -> tuple:
    return (
        post.event_start_at - timedelta(days=constants.DEFAULT_TIME_BEFORE_DAYS),
        post.event_end_at + timedelta(days=constants.DEFAULT_TIME_AFTER_DAYS),
    )


def _time_proximity(query_start, query_end, cand_start, cand_end) -> float:
    if not query_start or not query_end or not cand_start or not cand_end:
        return 0.0
    latest_start = max(query_start, cand_start)
    earliest_end = min(query_end, cand_end)
    if latest_start <= earliest_end:
        return 1.0
    gap_days = abs((latest_start - earliest_end).total_seconds()) / 86400
    return max(0.0, 1.0 - gap_days / constants.DEFAULT_TIME_AFTER_DAYS)


def _attr_match(query_brand: str, query_color: str, post: Post) -> bool:
    try:
        attr = post.attribute
    except PostAttribute.DoesNotExist:
        return False
    brand = (attr.brand or "").strip().lower()
    color = (attr.primary_color or "").strip().lower()
    q_brand = (query_brand or "").strip().lower()
    q_color = (query_color or "").strip().lower()
    brand_hit = bool(q_brand and brand and q_brand == brand)
    color_hit = bool(q_color and color and q_color == color)
    return brand_hit or color_hit


def _ready_vectors_by_post(post_ids: list[int]) -> dict[int, list[list[float]]]:
    if not post_ids:
        return {}
    rows = ImageEmbedding.objects.filter(
        post_id__in=post_ids,
        version=constants.EMBEDDING_VERSION,
        status=constants.STATUS_READY,
    ).exclude(vector=None)
    grouped: dict[int, list[list[float]]] = defaultdict(list)
    for row in rows:
        if isinstance(row.vector, list) and row.vector:
            grouped[row.post_id].append(row.vector)
    return grouped


def _max_vector_score(
    query_vectors: list[list[float]], candidate_vectors: list[list[float]]
) -> float:
    if not query_vectors or not candidate_vectors:
        return 0.0
    best = 0.0
    for qv in query_vectors:
        for cv in candidate_vectors:
            best = max(best, cosine_score(qv, cv))
    return best


def _build_reason(
    *,
    vector_score: float,
    l2_match: bool,
    l2_code: str | None,
    time_score: float,
    place_match: bool,
    attr_hit: bool,
    keyword_hit: bool,
) -> str:
    parts: list[str] = []
    if vector_score >= constants.VECTOR_REASON_THRESHOLD:
        parts.append("外观相似")
    if l2_match and l2_code:
        parts.append(f"同为{CATEGORY_L2_LABELS.get(l2_code, l2_code)}")
    if place_match:
        parts.append("同一场所")
    if attr_hit:
        parts.append("颜色或品牌一致")
    if time_score >= constants.TIME_REASON_THRESHOLD:
        parts.append("时间接近")
    if keyword_hit:
        parts.append("关键词命中")
    return " · ".join(parts) if parts else "综合匹配"


def embed_query_text(*, text: str, image_cos_key: str | None) -> list[float] | None:
    provider = get_provider()
    if not provider.is_available():
        return None
    text = (text or "").strip()
    image_cos_key = (image_cos_key or "").strip() or None
    if not text and not image_cos_key:
        return None
    cache_key = f"ai:query_emb:{source_hash(text, image_cos_key or '')}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    image_url = None
    if image_cos_key:
        try:
            from apps.storage.cos_presign import presign_original_get

            image_url = presign_original_get(
                image_cos_key, expired=constants.ORIGINAL_GET_EXPIRES
            )
        except Exception:
            if provider.name != constants.PROVIDER_FAKE:
                raise

    vector = provider.embed(text=text, image_url=image_url)
    cache.set(cache_key, vector, constants.QUERY_EMBED_CACHE_TTL)
    return vector


def _candidate_queryset(ctx: QueryContext) -> QuerySet:
    qs = Post.objects.select_related(
        "found_region", "found_place", "attribute"
    ).prefetch_related("images")
    qs = apply_post_hard_filters(
        qs,
        type=ctx.target_type,
        category_l1=ctx.category_l1,
        region_code=ctx.region_code,
        place_id=ctx.place_id,
        event_start=ctx.event_start,
        event_end=ctx.event_end,
    )
    if ctx.source_post is not None:
        qs = qs.exclude(pk=ctx.source_post.pk)
    return qs.order_by("-published_at", "-id")[: constants.HARD_FILTER_CAP]


def _score_post(ctx: QueryContext, post: Post, vector_score: float, keyword_hit: bool) -> RankedHit:
    l2_match = bool(ctx.query_l2 and post.category_l2 == ctx.query_l2)
    place_match = bool(
        ctx.query_place_id and post.found_place_id == ctx.query_place_id
    )
    time_score = _time_proximity(
        ctx.event_start, ctx.event_end, post.event_start_at, post.event_end_at
    )
    attr_hit = _attr_match(ctx.query_brand, ctx.query_color, post)
    score = (
        constants.WEIGHT_VECTOR * vector_score
        + constants.WEIGHT_CATEGORY_L2 * (1.0 if l2_match else 0.0)
        + constants.WEIGHT_TIME * time_score
        + constants.WEIGHT_PLACE * (1.0 if place_match else 0.0)
        + constants.WEIGHT_ATTR * (1.0 if attr_hit else 0.0)
    )
    reason = _build_reason(
        vector_score=vector_score,
        l2_match=l2_match,
        l2_code=post.category_l2 if l2_match else None,
        time_score=time_score,
        place_match=place_match,
        attr_hit=attr_hit,
        keyword_hit=keyword_hit,
    )
    return RankedHit(
        post=post,
        score=round(score, 6),
        vector_score=round(vector_score, 6),
        reason=reason,
        keyword_hit=keyword_hit,
    )


def _upsert_matches(ctx: QueryContext, hits: list[RankedHit]) -> list[RankedHit]:
    stored: list[RankedHit] = []
    for hit in hits[: constants.MATCH_STORE_LIMIT]:
        if ctx.source_post is None:
            existing = MatchCandidate.objects.filter(
                searcher_id=ctx.searcher_id,
                query_post__isnull=True,
                candidate_post=hit.post,
            ).first()
        else:
            existing = MatchCandidate.objects.filter(
                searcher_id=ctx.searcher_id,
                query_post=ctx.source_post,
                candidate_post=hit.post,
            ).first()
        defaults = {
            "score": hit.score,
            "vector_score": hit.vector_score,
            "reason": hit.reason,
        }
        if existing:
            existing.score = defaults["score"]
            existing.vector_score = defaults["vector_score"]
            existing.reason = defaults["reason"]
            existing.save(
                update_fields=["score", "vector_score", "reason", "updated_at"]
            )
            hit.match = existing
        else:
            hit.match = MatchCandidate.objects.create(
                searcher_id=ctx.searcher_id,
                query_post=ctx.source_post,
                candidate_post=hit.post,
                **defaults,
            )
        stored.append(hit)
    return stored


def build_query_context(
    *,
    searcher,
    source_post: Post | None,
    target_type: str | None,
    text: str,
    image_cos_key: str | None,
    category_l1: str | None,
    region_code: str | None,
    place_id: int | None,
    event_start,
    event_end,
    q: str,
) -> QueryContext:
    query_l2 = None
    query_place_id = None
    query_brand = ""
    query_color = ""
    query_vectors: list[list[float]] = []
    adhoc_text = (text or "").strip()

    if source_post is not None:
        target_type = opposite_type(source_post.type)
        if not category_l1:
            category_l1 = source_post.category_l1
        if not region_code:
            region_code = source_post.found_region.code
        if event_start is None or event_end is None:
            event_start, event_end = default_time_window(source_post)
        query_l2 = source_post.category_l2
        query_place_id = source_post.found_place_id
        try:
            attr = source_post.attribute
        except PostAttribute.DoesNotExist:
            attr = None
        if attr:
            query_brand = attr.brand or ""
            query_color = attr.primary_color or ""
        grouped = _ready_vectors_by_post([source_post.pk])
        query_vectors = grouped.get(source_post.pk, [])
        if not query_vectors and (adhoc_text or image_cos_key):
            extra = embed_query_text(text=adhoc_text, image_cos_key=image_cos_key)
            if extra:
                query_vectors = [extra]
    else:
        if target_type not in ("lost", "found"):
            raise ValueError("无源帖时必须指定 target_type")
        query_place_id = place_id
        extra = embed_query_text(text=adhoc_text, image_cos_key=image_cos_key)
        if extra:
            query_vectors = [extra]
        elif adhoc_text:
            # Fake/无 Key 时仍给一个可排序的退化向量：用文本指纹，检索侧当 0。
            query_vectors = []

    return QueryContext(
        searcher_id=searcher.pk,
        source_post=source_post,
        target_type=target_type,
        category_l1=category_l1,
        region_code=region_code,
        place_id=place_id,
        event_start=event_start,
        event_end=event_end,
        q=(q or "").strip(),
        query_vectors=query_vectors,
        query_l2=query_l2,
        query_place_id=query_place_id,
        query_brand=query_brand,
        query_color=query_color,
        adhoc_text=adhoc_text,
    )


def run_search(ctx: QueryContext) -> list[RankedHit]:
    qs = _candidate_queryset(ctx)
    posts = list(qs)
    if not posts:
        return []

    keyword_ids: set[int] = set()
    if ctx.q:
        keyword_ids = set(
            apply_post_search_query(
                Post.objects.filter(pk__in=[p.pk for p in posts]), ctx.q
            ).values_list("pk", flat=True)
        )

    vectors_by_post = _ready_vectors_by_post([p.pk for p in posts])
    has_any_ready = bool(vectors_by_post)
    has_query_vectors = bool(ctx.query_vectors)

    hits: list[RankedHit] = []
    for post in posts:
        keyword_hit = post.pk in keyword_ids
        cand_vectors = vectors_by_post.get(post.pk, [])
        vector_score = _max_vector_score(ctx.query_vectors, cand_vectors)

        if has_query_vectors and has_any_ready:
            keep = bool(cand_vectors) or keyword_hit
        elif ctx.q:
            keep = keyword_hit or not has_any_ready
        else:
            keep = True
        if not keep:
            continue
        hits.append(_score_post(ctx, post, vector_score, keyword_hit))

    hits.sort(key=lambda item: (item.score, item.vector_score, item.post.pk), reverse=True)
    return _upsert_matches(ctx, hits)


def list_saved_matches(post: Post, searcher) -> list[MatchCandidate]:
    return list(
        MatchCandidate.objects.select_related(
            "candidate_post",
            "candidate_post__found_region",
            "candidate_post__found_place",
            "candidate_post__attribute",
        )
        .prefetch_related("candidate_post__images")
        .filter(searcher=searcher, query_post=post)
        .order_by("-score", "-id")
    )
