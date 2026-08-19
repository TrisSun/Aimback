"""
限流（throttle）类集合。

B 负责账号鉴权/上传/限流这一块，三个高敏感接口都需要节流：
    - send-code：防同一 IP 对多个手机号各发一条（短信资源消耗攻击）
    - login-code：防验证码爆破（6 位码 10 万种组合）
    - upload/presign：防登录用户狂刷上传凭证（耗 COS 接口）

注意：
    1. 这一层是「安全节流」（per-IP / per-user），与 send-code 里手写的
       per-phone 业务节流（SEND_INTERVAL/DAILY_LIMIT）是独立维度，两层并存。
    2. 计数后端用 Django cache（开发期 locmem），部署阶段应切 Redis，
       否则多进程 / 多机会各自计数，限流失效。
"""
from rest_framework.throttling import SimpleRateThrottle


def _client_ip(request) -> str:
    """获取客户端 IP，依次尝试 X-Forwarded-For / REMOTE_ADDR。

    开发期直接用 REMOTE_ADDR；上线前应该只信任来自已知反向代理的 XFF，
    并配置 NUM_PROXIES，否则攻击者可伪造 XFF 绕过。
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # XFF 形如 "client, proxy1, proxy2"，第一个才是真实客户端
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "0.0.0.0"


class SendCodeIPThrottle(SimpleRateThrottle):
    """send-code：按客户端 IP 节流。

    默认 30/min（settings.REST_FRAMEWORK.DEFAULT_THROTTLE_RATES.send_code_ip）。
    """

    scope = "send_code_ip"

    def get_cache_key(self, request, view):
        return f"throttle:send_code_ip:{_client_ip(request)}"


class LoginIPThrottle(SimpleRateThrottle):
    """login-code：按客户端 IP 节流。

    默认 10/min。比 send-code 更严，因为 6 位验证码可枚举。
    """

    scope = "login_ip"

    def get_cache_key(self, request, view):
        return f"throttle:login_ip:{_client_ip(request)}"


class PresignUserThrottle(SimpleRateThrottle):
    """upload/presign：按登录用户节流。

    默认 30/min。匿名用户会被 IsAuthenticated 拦住，这里只数登录用户。
    """

    scope = "presign_user"

    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)
        # 匿名请求也会到这里（permission 层先 IsAuthenticated 拦，但写防御逻辑更稳）
        if not user or not getattr(user, "is_authenticated", False):
            # 用 IP 兜底，避免匿名也能把这条路径打满
            return f"throttle:presign_user:anon:{_client_ip(request)}"
        return f"throttle:presign_user:user:{user.pk}"
