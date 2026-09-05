from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.models import Post

from . import constants
from .models import Claim, ClaimAnswer, ClaimQuestion
from .serializers import ClaimDetailSerializer, ClaimPublicSerializer
from .services import generate_claim_questions


class ClaimConflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = '认领当前状态不允许该操作'
    default_code = 'conflict'


def _load_claim(pk):
    return get_object_or_404(
        Claim.objects.select_related(
            'post', 'post__author', 'claimant', 'post__custody_place'
        ).prefetch_related('answers__question'),
        pk=pk,
    )


def _set_post_status(post, new_status):
    post.status = new_status
    post.save(update_fields=['status', 'updated_at'])


class ClaimQuestionListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        questions = list(post.claim_questions.all())
        if not questions:
            generated = generate_claim_questions(post)
            questions = [
                ClaimQuestion.objects.create(post=post, question=q, sort_order=i)
                for i, q in enumerate(generated)
            ]
        data = [
            {'id': q.id, 'question': q.question, 'sort_order': q.sort_order}
            for q in questions
        ]
        return Response(data)


class ClaimCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user.id == post.author_id:
            raise PermissionDenied('不能认领自己的帖子')
        if post.status != 'published':
            raise ClaimConflict('该帖子当前不可认领')
        if Claim.objects.filter(post=post, status__in=constants.CLAIM_STATUS_ACTIVE).exists():
            raise ClaimConflict('该帖子已有进行中的认领')

        answers_data = request.data.get('answers') or []
        if not isinstance(answers_data, list):
            raise ValidationError({'answers': 'answers 必须是数组'})

        question_map = {}
        for item in answers_data:
            if not isinstance(item, dict):
                raise ValidationError({'answers': 'answers 每项必须是对象'})
            qid = item.get('question_id')
            question = ClaimQuestion.objects.filter(pk=qid, post=post).first()
            if question is None:
                raise ValidationError({'answers': f'问题 {qid} 不存在或不属于该帖子'})
            if qid in question_map:
                raise ValidationError({'answers': f'问题 {qid} 重复提交'})
            question_map[qid] = question

        claim = Claim.objects.create(post=post, claimant=request.user, status='pending')
        ClaimAnswer.objects.bulk_create([
            ClaimAnswer(
                claim=claim,
                question=question_map[item['question_id']],
                answer=(item.get('answer') or ''),
            )
            for item in answers_data
        ])

        _set_post_status(post, 'claiming')
        claim = _load_claim(claim.pk)
        return Response(ClaimPublicSerializer(claim).data, status=status.HTTP_201_CREATED)


class PostClaimListView(generics.ListAPIView):
    serializer_class = ClaimPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if self.request.user.id != post.author_id and not self.request.user.is_staff:
            raise PermissionDenied('只有作者可以查看认领列表')
        return Claim.objects.filter(post=post).select_related(
            'post', 'claimant'
        ).prefetch_related('answers__question')


class MyClaimListView(generics.ListAPIView):
    serializer_class = ClaimPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Claim.objects.filter(claimant=self.request.user).select_related(
            'post', 'claimant'
        ).prefetch_related('answers__question')


class ClaimDetailView(generics.RetrieveAPIView):
    serializer_class = ClaimDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        claim = _load_claim(self.kwargs['pk'])
        if self.request.user.id not in (claim.claimant_id, claim.post.author_id) and not self.request.user.is_staff:
            raise PermissionDenied('无权查看该认领')
        return claim


class ClaimApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        claim = _load_claim(pk)
        if request.user.id != claim.post.author_id:
            raise PermissionDenied('只有拾取者可以判定通过')
        if claim.status != 'pending':
            raise ClaimConflict('仅待判定状态可通过')
        claim.status = 'approved'
        claim.approved_at = timezone.now()
        claim.save(update_fields=['status', 'approved_at', 'updated_at'])
        return Response(ClaimDetailSerializer(claim).data)


class ClaimRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        claim = _load_claim(pk)
        if request.user.id != claim.post.author_id:
            raise PermissionDenied('只有拾取者可以判定拒绝')
        if claim.status != 'pending':
            raise ClaimConflict('仅待判定状态可拒绝')
        claim.status = 'rejected'
        claim.save(update_fields=['status', 'updated_at'])
        _set_post_status(claim.post, 'published')
        return Response(ClaimDetailSerializer(claim).data)


class ClaimCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        claim = _load_claim(pk)
        if request.user.id != claim.claimant_id:
            raise PermissionDenied('只有发起者可以撤回')
        if claim.status != 'pending':
            raise ClaimConflict('仅待判定状态可撤回')
        claim.status = 'cancelled'
        claim.save(update_fields=['status', 'updated_at'])
        _set_post_status(claim.post, 'published')
        return Response(ClaimDetailSerializer(claim).data)


class ClaimConfirmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        claim = _load_claim(pk)
        user_id = request.user.id
        if user_id not in (claim.claimant_id, claim.post.author_id):
            raise PermissionDenied('无权确认交接')
        if claim.status != 'approved':
            raise ClaimConflict('仅已通过状态可确认交接')

        if user_id == claim.post.author_id:
            claim.author_confirmed = True
        else:
            claim.claimant_confirmed = True

        update_fields = ['author_confirmed', 'claimant_confirmed', 'updated_at']

        if claim.author_confirmed and claim.claimant_confirmed:
            claim.status = 'completed'
            claim.completed_at = timezone.now()
            update_fields += ['status', 'completed_at']
            _set_post_status(claim.post, 'completed')

        claim.save(update_fields=update_fields)
        return Response(ClaimDetailSerializer(claim).data)
