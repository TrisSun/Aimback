from rest_framework.throttling import SimpleRateThrottle


def _client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "0.0.0.0"


class MatchSearchUserThrottle(SimpleRateThrottle):
    """matches/search：按登录用户节流，默认 20/min。"""

    scope = "match_search_user"

    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return f"throttle:match_search_user:anon:{_client_ip(request)}"
        return f"throttle:match_search_user:user:{user.pk}"
