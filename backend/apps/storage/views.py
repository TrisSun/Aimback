"""
图片上传与访问凭证接口。

路径约定（接口契约文档第 1 节）：
    Base URL = /api/v1/

实现端点：
    POST /api/v1/upload/presign/         图片上传签名凭证（给前端直传 COS）
    GET  /api/v1/upload/public-url/      cos_key → 可访问 URL（前端不自拼）
"""
import os

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.throttles import PresignUserThrottle

from .cos_presign import presign_original_upload, public_url_for

MAX_IMAGES_PER_POST = 4  # 接口契约 3.5：images 最多 4 张


class PresignUploadView(APIView):
    """
    给前端发「一次性上传许可证」。
    契约 3.5：images 最多 4 张（这里 1~MAX_IMAGES_PER_POST）。
    原图进私有桶；返回的 key 是 cos_key，前端 PUT 完后回传给 A 的帖子接口。
    """
    permission_classes = [permissions.IsAuthenticated]  # 已登录用户才能拿上传凭证
    throttle_classes = [PresignUserThrottle]  # 同一用户每分钟最多 30 次

    def post(self, request):
        try:
            count = int(request.data.get("count") or 1)
        except (TypeError, ValueError):
            return Response({"detail": "count 必须是整数。"}, status=400)
        if count < 1 or count > MAX_IMAGES_PER_POST:
            return Response(
                {"detail": f"count 必须在 1~{MAX_IMAGES_PER_POST} 之间。"},
                status=400,
            )
        content_type = (request.data.get("content_type") or "image/jpeg").strip()
        if not content_type.startswith("image/"):
            return Response({"detail": "只支持 image/* 类型。"}, status=400)
        tickets = [presign_original_upload(content_type) for _ in range(count)]
        return Response(
            {"count": len(tickets), "tickets": tickets, "expires_in": 300},
            status=200,
        )


class PublicUrlView(APIView):
    """
    cos_key → 浏览器可直接访问的 URL。
    契约 :11：前端不得拼接 COS 路径，必须由后端签发。
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        bucket = (request.query_params.get("bucket") or "").strip()
        key = (request.query_params.get("key") or "").strip()
        if not bucket or not key:
            return Response({"detail": "必须带 bucket 和 key 参数。"}, status=400)
        allowed = (
            os.environ.get("COS_BUCKET_ORIGINAL", ""),
            os.environ.get("COS_BUCKET_THUMB", ""),
        )
        if bucket not in allowed or not bucket:
            return Response({"detail": "未授权的 bucket。"}, status=400)
        return Response({"url": public_url_for(bucket, key)}, status=200)
