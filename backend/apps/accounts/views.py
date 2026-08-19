"""
账号鉴权接口。

路径约定（接口契约文档第 1 节）：
    Base URL = /api/v1/

实现端点：
    POST /api/v1/auth/send-code/         发验证码（自管 + dev 模式）
    POST /api/v1/auth/login-code/        用验证码登录；新手机号自动注册
    GET  /api/v1/auth/me/                当前登录用户信息（验证 token 用）
"""
import logging
import re

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import sms
from .auth_tokens import issue_token

log = logging.getLogger(__name__)
User = get_user_model()

PHONE_RE = re.compile(r"^1[3-9]\d{9}$")
SEND_INTERVAL = 60
DAILY_LIMIT = 10

CACHE_KEY_LAST = "sms:last:{phone}"
CACHE_KEY_DAILY = "sms:daily:{phone}:{day}"


def _today_str():
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d")


class SendCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = (request.data.get("phone") or "").strip()
        if not PHONE_RE.match(phone):
            return Response(
                {"detail": "手机号格式不对，必须是 11 位、以 1 开头。"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        last = cache.get(CACHE_KEY_LAST.format(phone=phone))
        if last:
            return Response(
                {"detail": "发送太频繁，请稍后再试。"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        today_key = CACHE_KEY_DAILY.format(phone=phone, day=_today_str())
        daily_count = cache.get(today_key, 0)
        if daily_count >= DAILY_LIMIT:
            return Response(
                {"detail": "今日发送次数已达上限，请明天再试。"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        # 先记限流（即使发送失败也占用一次额度，防刷）
        cache.set(CACHE_KEY_LAST.format(phone=phone), 1, SEND_INTERVAL)
        cache.set(today_key, daily_count + 1, 24 * 3600)

        # 发送验证码：通道内部生成码并存 cache（PNVS 由阿里云生成，dysms/dev 由本地生成）
        ok, code, err = sms.send_code(phone, cache)
        if not ok:
            return Response(
                {"detail": f"短信发送失败，请稍后重试。({err})"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        payload = {"msg": "验证码已发送"}
        # 开发模式（console 通道）把码写进响应便于联调
        if not sms.is_configured():
            payload["dev_code"] = code
        return Response(payload, status=status.HTTP_200_OK)


class LoginCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = (request.data.get("phone") or "").strip()
        code = (request.data.get("code") or "").strip()
        if not PHONE_RE.match(phone):
            return Response({"detail": "手机号格式不对。"}, status=400)
        if not re.match(r"^\d{6}$", code):
            return Response({"detail": "验证码格式不对。"}, status=400)
        if not sms.verify(phone, code, cache):
            return Response(
                {"detail": "验证码错误或已过期，请重试。"}, status=400
            )
        user, created = User.objects.get_or_create(username=phone)
        token = issue_token(user)
        return Response(
            {
                "token": token,
                "user": {"id": user.id, "phone": phone, "is_new": created},
            },
            status=200,
        )


class MeView(APIView):
    """用 token 验证登录态（前端 D 同学可用它确认 token 没失效）。"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({"id": u.id, "username": u.username})
