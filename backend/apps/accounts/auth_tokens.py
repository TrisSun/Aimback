"""
apps.accounts.auth_tokens
简单的 token 鉴权：自签不透明 token + django.core.cache。
"""
import secrets

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import authentication, exceptions

User = get_user_model()

TOKEN_TTL = 7 * 24 * 3600
CACHE_KEY = "auth:token:{token}"


def issue_token(user) -> str:
    token = secrets.token_urlsafe(32)
    cache.set(CACHE_KEY.format(token=token), user.id, TOKEN_TTL)
    return token


def parse_token(token: str):
    if not token:
        return None
    user_id = cache.get(CACHE_KEY.format(token=token))
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


class QueryTokenAuthentication(authentication.BaseAuthentication):
    """
    DRF 鉴权：?token=xxx 或 Authorization: Bearer xxx。
    MeView 用它来识别当前用户。
    """

    def authenticate(self, request):
        token = (
            request.query_params.get("token")
            or self._from_header(request)
        )
        if not token:
            return None
        user = parse_token(token)
        if not user:
            raise exceptions.AuthenticationFailed("token 无效或已过期。")
        return (user, token)

    @staticmethod
    def _from_header(request) -> str:
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.lower().startswith("bearer "):
            return auth[7:].strip()
        return ""