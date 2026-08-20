"""accounts app 的 Django Admin 配置。

设计要点：
1. 继承 DjangoUserAdmin 复用"修改密码"、"权限 checkbox"等现成表单
2. username 字段被我们用来存手机号，所以 list_display / search_fields /
   add_fieldsets 等都按手机号场景调整
3. 加 list_select_related 避免 N+1 查询（虽然 User 没外键，但保留习惯）
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # ---------- 列表页 ----------
    list_display = [
        "id",
        "username",      # 手机号
        "nickname",      # 昵称
        "is_active",
        "is_staff",
        "date_joined",
    ]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    search_fields = ["username", "nickname"]  # 按手机号或昵称搜
    ordering = ["-date_joined"]
    list_per_page = 30

    # ---------- 详情页（编辑用户时显示的字段分组） ----------
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "个人信息",
            {"fields": ("nickname", "avatar", "first_name", "last_name", "email")},
        ),
        (
            "权限",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("重要时间", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ["date_joined", "last_login"]

    # ---------- 新建用户时的表单 ----------
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
