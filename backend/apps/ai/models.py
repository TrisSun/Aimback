from django.conf import settings
from django.db import models

from apps.posts.models import Post, PostImage

from . import constants


class ImageEmbedding(models.Model):
    """每张图一条向量；无图帖用 post_image=null 存纯文本向量。"""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="embeddings",
        verbose_name="帖子",
    )
    post_image = models.ForeignKey(
        PostImage,
        on_delete=models.CASCADE,
        related_name="embeddings",
        verbose_name="帖子图片",
        null=True,
        blank=True,
    )
    vector = models.JSONField("向量", null=True, blank=True)
    provider = models.CharField("供应商", max_length=32, default=constants.PROVIDER_DASHSCOPE)
    model = models.CharField("模型", max_length=128, default=constants.MODEL_DASHSCOPE)
    dim = models.PositiveSmallIntegerField("维度", default=constants.EMBEDDING_DIM)
    version = models.CharField("版本", max_length=16, default=constants.EMBEDDING_VERSION)
    source_hash = models.CharField("源指纹", max_length=64, blank=True, db_index=True)
    status = models.CharField(
        "状态",
        max_length=16,
        choices=constants.EMBEDDING_STATUS_CHOICES,
        default=constants.STATUS_PENDING,
        db_index=True,
    )
    error = models.TextField("错误", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "image_embeddings"
        verbose_name = "图片向量"
        verbose_name_plural = "图片向量"
        indexes = [
            models.Index(fields=["status", "version"], name="emb_status_version_idx"),
            models.Index(fields=["post", "status"], name="emb_post_status_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["post_image", "provider", "model", "dim", "version"],
                condition=models.Q(post_image__isnull=False),
                name="uniq_embedding_per_image_version",
            ),
            models.UniqueConstraint(
                fields=["post", "provider", "model", "dim", "version"],
                condition=models.Q(post_image__isnull=True),
                name="uniq_text_embedding_per_post_version",
            ),
        ]

    def __str__(self) -> str:
        return f"emb-{self.pk}-post-{self.post_id}-{self.status}"


class MatchCandidate(models.Model):
    """按需搜寻结果。feedback 在再次搜寻时保留。"""

    searcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="match_searches",
        verbose_name="搜寻者",
    )
    query_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="outgoing_matches",
        verbose_name="源帖",
        null=True,
        blank=True,
    )
    candidate_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="incoming_matches",
        verbose_name="候选帖",
    )
    score = models.FloatField("综合分", default=0)
    vector_score = models.FloatField("向量分", default=0)
    reason = models.CharField("匹配理由", max_length=255, blank=True)
    feedback = models.CharField(
        "用户反馈",
        max_length=16,
        choices=constants.FEEDBACK_CHOICES,
        default=constants.FEEDBACK_NONE,
        blank=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "match_candidates"
        verbose_name = "匹配候选"
        verbose_name_plural = "匹配候选"
        ordering = ["-score", "-id"]
        indexes = [
            models.Index(fields=["query_post", "-score"], name="match_query_score_idx"),
            models.Index(fields=["searcher", "-created_at"], name="match_searcher_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["searcher", "query_post", "candidate_post"],
                condition=models.Q(query_post__isnull=False),
                name="uniq_match_per_query_post",
            ),
            models.UniqueConstraint(
                fields=["searcher", "candidate_post"],
                condition=models.Q(query_post__isnull=True),
                name="uniq_adhoc_match_per_searcher_candidate",
            ),
        ]

    def __str__(self) -> str:
        return f"match-{self.pk}-cand-{self.candidate_post_id}"
