from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自定义用户：手机号登录。

    - username 存手机号（保持 accounts 鉴权 get_or_create(username=phone) 逻辑不变）
    - 契约未定用户字段，先最简：昵称 + 头像（均可空），后续需要再加
    - A 的 posts.Post.author 用 settings.AUTH_USER_MODEL 引用本模型
    """
    nickname = models.CharField("昵称", max_length=32, blank=True)
    avatar = models.URLField("头像", blank=True)

    class Meta:
        db_table = "users"
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username
