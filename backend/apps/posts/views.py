from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import apply_post_hard_filters
from .models import Post
from .serializers import PostPublicSerializer, PostWriteSerializer


class PostPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


def _parse_datetime(value: str):
    if not value:
        return None
    try:
        return serializers.DateTimeField().run_validation(value)
    except serializers.ValidationError:
        raise ValidationError({"detail": "时间参数格式不正确"})


def _parse_int(value: str) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError({"detail": "place_id 参数格式不正确"})


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostPublicSerializer
    pagination_class = PostPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostWriteSerializer
        return PostPublicSerializer

    def get_queryset(self):
        qs = Post.objects.select_related(
            "found_region", "found_place", "attribute"
        ).prefetch_related("images")
        return apply_post_hard_filters(
            qs,
            type=self.request.query_params.get("type"),
            category_l1=self.request.query_params.get("category_l1"),
            category_l2=self.request.query_params.get("category_l2"),
            region_code=self.request.query_params.get("region_code"),
            place_id=_parse_int(self.request.query_params.get("place_id")),
            event_start=_parse_datetime(self.request.query_params.get("event_start")),
            event_end=_parse_datetime(self.request.query_params.get("event_end")),
        )

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        post = write_serializer.save(author=request.user)
        public_serializer = PostPublicSerializer(
            post, context=self.get_serializer_context()
        )
        return Response(public_serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.GenericAPIView):
    serializer_class = PostPublicSerializer

    def get_queryset(self):
        return Post.objects.select_related(
            "found_region", "found_place", "attribute"
        ).prefetch_related("images")

    def _get_post(self, pk: int) -> Post:
        post = get_object_or_404(self.get_queryset(), pk=pk)
        if post.status == "draft" and post.author_id != self.request.user.id:
            raise PermissionDenied("草稿仅作者本人可见")
        return post

    def get(self, request, *args, **kwargs):
        post = self._get_post(kwargs["pk"])
        return Response(self.get_serializer(post).data)

    def patch(self, request, *args, **kwargs):
        post = self._get_post(kwargs["pk"])
        if post.author_id != request.user.id:
            raise PermissionDenied("只能修改自己的帖子")
        if post.status in ("completed", "closed"):
            raise ValidationError({"detail": "已完成或已关闭的帖子不可修改"})

        serializer = PostWriteSerializer(
            post, data=request.data, partial=True, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response(self.get_serializer(post).data)


class PostPublishView(generics.GenericAPIView):
    serializer_class = PostPublicSerializer

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs["pk"])
        if post.author_id != request.user.id:
            raise PermissionDenied("只能发布自己的帖子")
        if post.status != "draft":
            raise ValidationError({"detail": "仅草稿状态可以发布"})

        post.status = "published"
        post.published_at = timezone.now()
        post.save(update_fields=["status", "published_at", "updated_at"])
        return Response(self.get_serializer(post).data)


class PostCloseView(generics.GenericAPIView):
    serializer_class = PostPublicSerializer

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs["pk"])
        if post.author_id != request.user.id and not request.user.is_staff:
            raise PermissionDenied("只能关闭自己的帖子")
        if post.status not in ("closed", "completed"):
            post.status = "closed"
            post.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(post).data)
