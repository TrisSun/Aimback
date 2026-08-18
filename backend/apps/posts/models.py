from django.conf import settings
from django.db import models

from . import constants


class Region(models.Model):
    code = models.CharField("行政区代码", max_length=32, unique=True)
    name = models.CharField("名称", max_length=64)
    level = models.CharField(
        "级别", max_length=16, choices=constants.REGION_LEVEL_CHOICES
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name="上级行政区",
    )

    class Meta:
        db_table = "regions"
        ordering = ["code"]
        verbose_name = "行政区"
        verbose_name_plural = "行政区"

    def __str__(self) -> str:
        return f"{self.name}（{self.code}）"


class Place(models.Model):
    name = models.CharField("场所名称", max_length=128)
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT, related_name="places", verbose_name="所属行政区"
    )
    place_type = models.CharField(
        "场所类型",
        max_length=32,
        choices=constants.PLACE_TYPE_CHOICES,
        default="other",
    )
    address = models.CharField("地址", max_length=255, blank=True)
    latitude = models.DecimalField(
        "纬度", max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        "经度", max_digits=9, decimal_places=6, null=True, blank=True
    )
    is_active = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "places"
        ordering = ["id"]
        verbose_name = "场所"
        verbose_name_plural = "场所"

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="作者",
    )
    type = models.CharField(
        "类型", max_length=16, choices=constants.POST_TYPE_CHOICES
    )
    status = models.CharField(
        "状态",
        max_length=16,
        choices=constants.POST_STATUS_CHOICES,
        default="draft",
        db_index=True,
    )
    category_l1 = models.CharField(
        "一级分类",
        max_length=32,
        choices=constants.CATEGORY_L1_CHOICES,
        db_index=True,
    )
    category_l2 = models.CharField(
        "二级分类", max_length=32, choices=constants.CATEGORY_L2_CHOICES
    )
    title = models.CharField("标题", max_length=120, blank=True, null=True)
    description = models.TextField("描述")
    found_region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="found_posts",
        verbose_name="发现行政区",
    )
    found_place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="found_posts",
        verbose_name="发现场所",
    )
    found_location_lat = models.DecimalField(
        "发现纬度", max_digits=9, decimal_places=6, null=True, blank=True
    )
    found_location_lng = models.DecimalField(
        "发现经度", max_digits=9, decimal_places=6, null=True, blank=True
    )
    custody_type = models.CharField(
        "保管方式",
        max_length=16,
        choices=constants.CUSTODY_TYPE_CHOICES,
        default="personal",
    )
    custody_place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="custody_posts",
        verbose_name="保管场所",
    )
    custody_address = models.CharField("保管地址", max_length=255, blank=True)
    event_start_at = models.DateTimeField("时间窗口起点")
    event_end_at = models.DateTimeField("时间窗口终点")
    published_at = models.DateTimeField("发布时间", null=True, blank=True, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]
        verbose_name = "帖子"
        verbose_name_plural = "帖子"
        indexes = [
            models.Index(fields=["type", "status"], name="post_type_status_idx"),
            models.Index(fields=["category_l1", "status"], name="post_cat1_status_idx"),
            models.Index(fields=["event_start_at", "event_end_at"], name="post_event_idx"),
        ]

    def __str__(self) -> str:
        return self.title or f"{self.get_type_display()}-{self.pk}"


class PostImage(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="images", verbose_name="帖子"
    )
    cos_key = models.CharField("对象存储键", max_length=512)
    sort_order = models.PositiveSmallIntegerField("顺序", default=0)
    review_status = models.CharField(
        "审核状态",
        max_length=16,
        choices=constants.REVIEW_STATUS_CHOICES,
        default="pending",
        db_index=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "post_images"
        ordering = ["sort_order", "id"]
        verbose_name = "帖子图片"
        verbose_name_plural = "帖子图片"

    def __str__(self) -> str:
        return f"post-{self.post_id}-image-{self.pk}"


class PostAttribute(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="attribute", verbose_name="帖子"
    )
    brand = models.CharField("品牌", max_length=64, blank=True)
    primary_color = models.CharField("主色", max_length=64, blank=True)
    text_mark = models.CharField("文字标识", max_length=128, blank=True)
    distinctive_features = models.TextField("显著特征", blank=True)
    normalized_description = models.TextField("规范化描述", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "post_attributes"
        verbose_name = "帖子结构化属性"
        verbose_name_plural = "帖子结构化属性"

    def __str__(self) -> str:
        return f"post-{self.post_id}-attribute"
