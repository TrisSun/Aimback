from django.conf import settings
from django.db import models

from apps.posts.models import Post

from . import constants


class ClaimQuestion(models.Model):
    '''隐藏特征问题：由 AI 根据物品详情自动生成，无标准答案。'''
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='claim_questions', verbose_name='帖子'
    )
    question = models.CharField('问题', max_length=255)
    sort_order = models.PositiveSmallIntegerField('顺序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'claim_questions'
        ordering = ['sort_order', 'id']
        verbose_name = '隐藏特征问题'
        verbose_name_plural = '隐藏特征问题'

    def __str__(self):
        return f'post-{self.post_id}-question-{self.pk}'


class Claim(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='claims', verbose_name='帖子'
    )
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='claims',
        verbose_name='失主',
    )
    status = models.CharField(
        '状态', max_length=16, choices=constants.CLAIM_STATUS_CHOICES, default='pending', db_index=True
    )
    author_confirmed = models.BooleanField('拾取者已确认', default=False)
    claimant_confirmed = models.BooleanField('失主已确认', default=False)
    approved_at = models.DateTimeField('通过时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'claims'
        ordering = ['-created_at']
        verbose_name = '认领'
        verbose_name_plural = '认领'
        constraints = [
            models.UniqueConstraint(
                fields=['post'],
                condition=models.Q(status__in=['pending', 'approved']),
                name='unique_active_claim_per_post',
            ),
        ]

    def __str__(self):
        return f'claim-{self.pk}-post-{self.post_id}'


class ClaimAnswer(models.Model):
    '''失主针对隐藏问题的回答。'''
    claim = models.ForeignKey(
        Claim, on_delete=models.CASCADE, related_name='answers', verbose_name='认领'
    )
    question = models.ForeignKey(
        ClaimQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name='问题'
    )
    answer = models.TextField('回答')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'claim_answers'
        verbose_name = '认领回答'
        verbose_name_plural = '认领回答'

    def __str__(self):
        return f'claim-{self.claim_id}-answer-{self.pk}'
