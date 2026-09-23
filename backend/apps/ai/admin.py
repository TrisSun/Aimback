from django.contrib import admin

from .models import ImageEmbedding, MatchCandidate


@admin.register(ImageEmbedding)
class ImageEmbeddingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "post",
        "post_image",
        "status",
        "provider",
        "model",
        "dim",
        "version",
        "updated_at",
    ]
    list_filter = ["status", "provider", "version"]
    search_fields = ["post__title", "post__description", "error"]
    list_select_related = ["post", "post_image"]
    raw_id_fields = ["post", "post_image"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"


@admin.register(MatchCandidate)
class MatchCandidateAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "searcher",
        "query_post",
        "candidate_post",
        "score",
        "vector_score",
        "feedback",
        "updated_at",
    ]
    list_filter = ["feedback"]
    search_fields = ["reason", "searcher__username"]
    list_select_related = ["searcher", "query_post", "candidate_post"]
    raw_id_fields = ["searcher", "query_post", "candidate_post"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
