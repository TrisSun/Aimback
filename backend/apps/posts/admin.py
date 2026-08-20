"""posts app 的 Django Admin 配置。

设计要点（基于 A 的初始版本扩展）：
1. list_select_related 避免 N+1：列表页会显示外键字段（author / region / place）
2. raw_id_fields 用搜索框代替下拉：Region / Place 数据量大时下拉会卡
3. date_hierarchy 按日期层级浏览：运营人员按天审核帖子
4. readonly_fields 自动字段不可改：created_at / updated_at / published_at
5. 单独注册 PostImage：图片除了从 Post 详情看，也要有独立列表页
"""
from django.contrib import admin

from .models import Place, Post, PostAttribute, PostImage, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "level", "parent"]
    list_filter = ["level"]
    search_fields = ["code", "name"]
    list_select_related = ["parent"]  # N+1 优化


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "region", "place_type", "is_active", "created_at"]
    list_filter = ["place_type", "is_active", "region"]
    search_fields = ["name", "address"]
    list_select_related = ["region"]
    raw_id_fields = ["region"]  # Region 数据量大，避免下拉
    date_hierarchy = "created_at"
    list_per_page = 50


class PostImageInline(admin.TabularInline):
    """Post 详情页底部的图片内联编辑。"""
    model = PostImage
    extra = 0
    fields = ["cos_key", "sort_order", "review_status"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "type",
        "status",
        "category_l1",
        "category_l2",
        "title",
        "author",
        "found_region",
        "created_at",
    ]
    list_filter = ["type", "status", "category_l1", "custody_type", "found_region"]
    search_fields = ["title", "description", "author__username"]
    list_select_related = [
        "author", "found_region", "found_place", "custody_place",
    ]
    raw_id_fields = ["author", "found_region", "found_place", "custody_place"]
    date_hierarchy = "created_at"
    list_per_page = 30
    inlines = [PostImageInline]
    readonly_fields = ["created_at", "updated_at", "published_at"]


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """PostImage 单独注册：除了从 Post 详情看，也要有独立列表页方便按图片维度审核。"""
    list_display = ["id", "post", "cos_key", "sort_order", "review_status", "created_at"]
    list_filter = ["review_status"]
    search_fields = ["cos_key", "post__title"]
    list_select_related = ["post"]
    raw_id_fields = ["post"]
    date_hierarchy = "created_at"


@admin.register(PostAttribute)
class PostAttributeAdmin(admin.ModelAdmin):
    list_display = ["post", "brand", "primary_color", "text_mark"]
    search_fields = ["brand", "primary_color", "text_mark", "normalized_description"]
    list_select_related = ["post"]
    raw_id_fields = ["post"]
