from __future__ import annotations

import logging
import sys
import threading

from django.conf import settings
from django.db import transaction

from apps.posts.constants import POST_STATUS_SEARCHABLE
from apps.posts.models import Post, PostAttribute, PostImage

from . import constants
from .models import ImageEmbedding
from .providers import get_provider
from .providers.base import EmbeddingError
from .vectors import source_hash

logger = logging.getLogger(__name__)


def _is_testing() -> bool:
    return any(arg == "test" or arg.startswith("test") for arg in sys.argv)


def build_post_text(post: Post) -> str:
    parts = [post.title or "", post.description or ""]
    try:
        attr = post.attribute
    except PostAttribute.DoesNotExist:
        attr = None
    if attr:
        parts.extend(
            [
                attr.brand or "",
                attr.primary_color or "",
                attr.text_mark or "",
                attr.distinctive_features or "",
                attr.normalized_description or "",
            ]
        )
    return "\n".join(item.strip() for item in parts if item and str(item).strip())


def _current_meta() -> dict:
    provider = get_provider()
    return {
        "provider": provider.name,
        "model": (
            constants.MODEL_DASHSCOPE
            if provider.name == constants.PROVIDER_DASHSCOPE
            else constants.PROVIDER_FAKE
        ),
        "dim": constants.EMBEDDING_DIM,
        "version": constants.EMBEDDING_VERSION,
    }


def _upsert_pending(post: Post, post_image: PostImage | None, digest: str) -> ImageEmbedding:
    meta = _current_meta()
    lookup = {
        "post": post,
        "post_image": post_image,
        "provider": meta["provider"],
        "model": meta["model"],
        "dim": meta["dim"],
        "version": meta["version"],
    }
    obj = ImageEmbedding.objects.filter(**lookup).first()
    if obj is None:
        return ImageEmbedding.objects.create(
            **lookup,
            source_hash=digest,
            status=constants.STATUS_PENDING,
            vector=None,
            error="",
        )
    if (
        obj.source_hash == digest
        and obj.status == constants.STATUS_READY
        and obj.vector
    ):
        return obj
    obj.source_hash = digest
    obj.status = constants.STATUS_PENDING
    obj.vector = None
    obj.error = ""
    obj.save(update_fields=["source_hash", "status", "vector", "error", "updated_at"])
    return obj


def sync_post_embeddings(post: Post) -> None:
    """按当前图片/文本对齐 pending 行。草稿不同步。"""
    if post.status not in POST_STATUS_SEARCHABLE:
        return

    if not hasattr(post, "_state"):
        return

    post = (
        Post.objects.select_related("attribute")
        .prefetch_related("images")
        .get(pk=post.pk)
    )
    text = build_post_text(post)
    images = list(post.images.all())
    meta = _current_meta()
    version_qs = ImageEmbedding.objects.filter(post=post, version=meta["version"])

    if images:
        version_qs.filter(post_image__isnull=True).delete()
        keep_ids = []
        for image in images:
            digest = source_hash(text, image.cos_key)
            row = _upsert_pending(post, image, digest)
            keep_ids.append(row.post_image_id)
        version_qs.filter(post_image__isnull=False).exclude(
            post_image_id__in=keep_ids
        ).delete()
    else:
        version_qs.exclude(post_image__isnull=True).delete()
        digest = source_hash(text, "")
        _upsert_pending(post, None, digest)


def _presign_image(image: PostImage) -> str | None:
    from apps.storage.cos_presign import presign_original_get

    return presign_original_get(image.cos_key, expired=constants.ORIGINAL_GET_EXPIRES)


def process_pending(*, limit: int = 20, post_id: int | None = None) -> int:
    """处理 pending 向量。返回成功条数。"""
    provider = get_provider()
    if not provider.is_available():
        logger.info("embedding provider 不可用，跳过 process_pending")
        return 0

    qs = ImageEmbedding.objects.select_related("post", "post__attribute", "post_image").filter(
        status=constants.STATUS_PENDING,
        version=constants.EMBEDDING_VERSION,
    )
    if post_id is not None:
        qs = qs.filter(post_id=post_id)
    rows = list(qs.order_by("id")[:limit])
    success = 0
    for row in rows:
        text = build_post_text(row.post)
        image_url = None
        try:
            if row.post_image_id:
                try:
                    image_url = _presign_image(row.post_image)
                except Exception as exc:
                    if provider.name != constants.PROVIDER_FAKE:
                        raise EmbeddingError(f"签发原图 URL 失败: {exc}") from exc
            vector = provider.embed(text=text, image_url=image_url)
            row.vector = vector
            row.status = constants.STATUS_READY
            row.error = ""
            row.save(update_fields=["vector", "status", "error", "updated_at"])
            success += 1
        except Exception as exc:
            logger.exception("向量化失败 embedding=%s post=%s", row.pk, row.post_id)
            row.status = constants.STATUS_FAILED
            row.error = str(exc)[:2000]
            row.save(update_fields=["status", "error", "updated_at"])
    return success


def sync_searchable_posts() -> int:
    count = 0
    qs = Post.objects.filter(status__in=POST_STATUS_SEARCHABLE).only("id", "status")
    for post in qs.iterator():
        sync_post_embeddings(post)
        count += 1
    return count


def schedule_embed(post_id: int) -> None:
    """发布后尽快处理：测试环境跳过线程；INLINE 同步；否则 on_commit 后台线程。"""
    if _is_testing() and not getattr(settings, "AI_EMBED_INLINE", False):
        return

    def _run() -> None:
        try:
            process_pending(limit=20, post_id=post_id)
        except Exception:
            logger.exception("后台向量化失败 post=%s", post_id)

    if getattr(settings, "AI_EMBED_INLINE", False):
        _run()
        return

    transaction.on_commit(lambda: threading.Thread(target=_run, daemon=True).start())


def sync_and_schedule(post: Post) -> None:
    sync_post_embeddings(post)
    if post.status in POST_STATUS_SEARCHABLE:
        schedule_embed(post.pk)
