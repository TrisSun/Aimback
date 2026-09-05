import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "True").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.posts.apps.PostsConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.storage.apps.StorageConfig",
    "apps.claims.apps.ClaimsConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# 本地开发默认 SQLite；PostgreSQL 连接与 pgvector 由 B 在 infra 中落地。
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
# 静态文件收集目录：生产服务器在 .env 里覆盖为绝对路径（如 /var/www/aimback/static）
STATIC_ROOT = os.environ.get("STATIC_ROOT") or str(BASE_DIR / "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.auth_tokens.QueryTokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    # 限流：速率表，仅供各视图显式声明 throttle_classes 时查询。
    # 故意不设 DEFAULT_THROTTLE_CLASSES，避免全局默认拦截读接口。
    "DEFAULT_THROTTLE_RATES": {
        "send_code_ip": "30/min",   # send-code：同一 IP 每分钟最多 30 次，防刷多手机号
        "login_ip":     "10/min",   # login-code：同一 IP 每分钟最多 10 次，防验证码爆破
        "presign_user": "30/min",   # presign：同一登录用户每分钟最多 30 张上传凭证
    },
}

# 自定义用户模型（B 建 apps/accounts.User 后启用）。
# posts 模型引用 settings.AUTH_USER_MODEL，迁移会自动跟随切换。
AUTH_USER_MODEL = "accounts.User"

# 缓存后端：env 驱动，REDIS_URL 填了走 Redis（生产/联调），空则 locmem（本地开发兜底）。
# 用途：DRF throttle 计数 / token 缓存 / 短信验证码 / 短信发送频率。
# ⚠️ locmem 是进程内缓存，跨进程不共享（多 worker 部署时 throttle 会失效）。
REDIS_URL = os.environ.get("REDIS_URL", "").strip()
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "aimback",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "aimback-dev",
        }
    }

# CORS：env 驱动。开发期默认全放开（前端联调）；生产 .env 设置
#   CORS_ALLOW_ALL_ORIGINS=false
#   CORS_ALLOWED_ORIGINS=https://example.com,http://118.25.145.183
# 来收紧到具体来源（注意：CORS_ALLOW_ALL_ORIGINS=true 时白名单不生效）。
CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "true").lower() == "true"
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
