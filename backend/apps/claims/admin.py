from django.contrib import admin

from .models import Claim, ClaimAnswer, ClaimQuestion


@admin.register(ClaimQuestion)
class ClaimQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'question', 'sort_order')
    list_filter = ('post',)
    search_fields = ('question',)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'claimant', 'status', 'author_confirmed', 'claimant_confirmed', 'created_at')
    list_filter = ('status',)
    search_fields = ('post__title', 'claimant__username')


@admin.register(ClaimAnswer)
class ClaimAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'claim', 'question', 'answer')
