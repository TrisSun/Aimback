"""
图片上传与访问凭证接口。

路径约定（接口契约文档第 1 节）：
    Base URL = /api/v1/

实现端点：
    POST /api/v1/upload/presign/         图片上传签名凭证（给前端直传 COS）
    GET  /api/v1/upload/public-url/      cos_key → 可访问 URL（缩略图直连 / 原图签名）
"""
import re

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.throttles import PresignUserThrottle

from .cos_presign import (
    presign_original_get,
    presign_original_upload,
    thumb_url_for,
)

MAX_IMAGES_PER_POST = 4  # 接口契约 3.5：images 最多 4 张

# 原图 key 白名单格式：posts/YYYY/MM/{32位hex}.{jpg|png|webp|gif|bmp}
# 防止用 public-url 接口读取桶内任意对象（如其他路径的敏感文件）。
KEY_RE = re.compile(r"^posts/\d{4}/\d{2}/[0-9a-f]{32}\.(jpg|png|webp|gif|bmp)$")


class PresignUploadView(APIView):
    """
    给前端发「一次性上传许可证」。
    契约 3.5：images 最多 4 张（这里 1~MAX_IMAGES_PER_POST）。
    原图进私有桶，COS 上传后自动生成缩略图到公有桶；
    返回的 cos_key 前端 PUT 完后回传给 A 的帖子接口。
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
    契约 §1：前端不得拼接 COS 路径，必须由后端签发。

    参数：
        key  原图 cos_key（必填，白名单校验）
        size thumb（默认，缩略图公有桶直连）| original（原图私有桶签名）
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        key = (request.query_params.get("key") or "").strip()
        size = (request.query_params.get("size") or "thumb").strip()

        if not key:
            return Response({"detail": "必须带 key 参数。"}, status=400)
        if not KEY_RE.match(key):
            return Response({"detail": "非法的 key。"}, status=400)
        if size not in {"thumb", "original"}:
            return Response({"detail": "size 只支持 thumb 或 original。"}, status=400)

        if size == "original":
            url = presign_original_get(key)
        else:
            url = thumb_url_for(key)

        return Response({"url": url, "key": key, "size": size}, status=200)
