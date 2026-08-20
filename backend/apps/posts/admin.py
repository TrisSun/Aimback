from django.contrib import admin

from .models import Place, Post, PostAttribute, PostImage, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "level", "parent"]
    search_fields = ["code", "name"]
    list_filter = ["level"]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "region", "place_type", "is_active"]
    search_fields = ["name"]
    list_filter = ["place_type", "is_active"]


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "type",
        "status",
        "category_l1",
        "category_l2",
        "title",
        "created_at",
    ]
    list_filter = ["type", "status", "category_l1", "custody_type"]
    search_fields = ["title", "description"]
    inlines = [PostImageInline]


@admin.register(PostAttribute)
class PostAttributeAdmin(admin.ModelAdmin):
    list_display = ["post", "brand", "primary_color"]
    search_fields = ["brand", "primary_color", "text_mark"]
