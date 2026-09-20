from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.models import Post

from . import constants
from .models import MatchCandidate
from .search import build_query_context, list_saved_matches, run_search
from .serializers import (
    MatchFeedbackSerializer,
    MatchResultSerializer,
    MatchSearchSerializer,
    SavedMatchSerializer,
)
from .throttles import MatchSearchUserThrottle


def _serialize_hits(hits, *, page: int, page_size: int) -> dict:
    total = len(hits)
    start = (page - 1) * page_size
    page_hits = hits[start : start + page_size]
    payload = []
    for hit in page_hits:
        match = hit.match
        payload.append(
            {
                "match_id": match.pk if match else None,
                "score": hit.score,
                "vector_score": hit.vector_score,
                "reason": hit.reason,
                "feedback": match.feedback if match else "",
                "post": hit.post,
            }
        )
    return {
        "count": total,
        "page": page,
        "page_size": page_size,
        "results": MatchResultSerializer(payload, many=True).data,
    }


class MatchSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [MatchSearchUserThrottle]

    def post(self, request):
        serializer = MatchSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        source_post = None
        source_id = data.get("source_post_id")
        if source_id:
            source_post = get_object_or_404(
                Post.objects.select_related(
                    "found_region", "found_place", "attribute"
                ).prefetch_related("images"),
                pk=source_id,
            )
            if source_post.author_id != request.user.id:
                raise PermissionDenied("只能用自己的帖子发起搜寻")

        try:
            ctx = build_query_context(
                searcher=request.user,
                source_post=source_post,
                target_type=data.get("target_type"),
                text=data.get("text") or "",
                image_cos_key=data.get("image_cos_key") or None,
                category_l1=data.get("category_l1") or None,
                region_code=data.get("region_code") or None,
                place_id=data.get("place_id"),
                event_start=data.get("event_start"),
                event_end=data.get("event_end"),
                q=data.get("q") or "",
            )
            hits = run_search(ctx)
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc
        except Exception as exc:
            message = str(exc)
            if "签发" in message or "百炼" in message or "COS" in message:
                raise ValidationError({"detail": message}) from exc
            raise

        return Response(
            _serialize_hits(
                hits,
                page=data.get("page") or 1,
                page_size=data.get("page_size") or 20,
            )
        )


class MatchFeedbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        match = get_object_or_404(MatchCandidate, pk=pk)
        if match.searcher_id != request.user.id:
            raise PermissionDenied("只能标记自己的搜寻结果")
        serializer = MatchFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        label = serializer.validated_data["label"]
        match.feedback = (
            constants.FEEDBACK_NONE
            if label == "reset"
            else constants.FEEDBACK_NOT_MATCH
        )
        match.save(update_fields=["feedback", "updated_at"])
        return Response(
            {
                "match_id": match.pk,
                "feedback": match.feedback,
            }
        )


class PostMatchListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        post = get_object_or_404(Post, pk=pk)
        if post.author_id != request.user.id:
            raise PermissionDenied("只能查看自己帖子的匹配候选")
        matches = list_saved_matches(post, request.user)
        page = 1
        try:
            page = max(1, int(request.query_params.get("page") or 1))
        except (TypeError, ValueError):
            raise ValidationError({"page": "页码格式不正确"})
        try:
            page_size = int(request.query_params.get("page_size") or 20)
        except (TypeError, ValueError):
            raise ValidationError({"page_size": "每页条数格式不正确"})
        page_size = min(50, max(1, page_size))
        start = (page - 1) * page_size
        page_rows = matches[start : start + page_size]
        return Response(
            {
                "count": len(matches),
                "page": page,
                "page_size": page_size,
                "results": SavedMatchSerializer(page_rows, many=True).data,
            }
        )
