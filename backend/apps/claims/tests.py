from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.posts.models import Post, Region

User = get_user_model()


class ClaimFlowTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='13800000001')
        self.claimant = User.objects.create_user(username='13800000002')
        self.region = Region.objects.create(code='440305', name='南山区', level='district')
        self.post = Post.objects.create(
            author=self.author,
            type='found',
            status='published',
            category_l1='electronics',
            category_l2='phone',
            description='图书馆捡到一部黑色手机',
            found_region=self.region,
            event_start_at=timezone.now(),
            event_end_at=timezone.now(),
            published_at=timezone.now(),
        )

    def _set_questions(self, user, questions):
        self.client.force_authenticate(user=user)
        return self.client.put(
            f'/api/v1/posts/{self.post.id}/claim-questions',
            {'questions': [{'question': q} for q in questions]},
            format='json',
        )

    def _claim(self, user, answers=None):
        self.client.force_authenticate(user=user)
        return self.client.post(
            f'/api/v1/posts/{self.post.id}/claim', {'answers': answers or []}, format='json'
        )

    def test_set_and_get_questions(self):
        resp = self._set_questions(self.author, ['手机壳背面贴了什么？', '耳机盒里还有什么？'])
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        # 公开获取，且不含答案字段
        self.client.force_authenticate(user=None)
        resp = self.client.get(f'/api/v1/posts/{self.post.id}/claim-questions')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        self.assertNotIn('answer', resp.data[0])

    def test_only_author_can_set_questions(self):
        resp = self._set_questions(self.claimant, ['问题'])
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_claim_with_answers(self):
        self._set_questions(self.author, ['手机壳背面贴了什么？'])
        self.client.force_authenticate(user=None)
        qs = self.client.get(f'/api/v1/posts/{self.post.id}/claim-questions').data
        qid = qs[0]['id']
        resp = self._claim(self.claimant, [{'question_id': qid, 'answer': '柴犬贴纸'}])
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'claiming')

    def test_cannot_claim_own_post(self):
        resp = self._claim(self.author)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_claim_conflict(self):
        self._claim(self.claimant)
        resp = self._claim(self.claimant)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_reject_releases_post(self):
        resp = self._claim(self.claimant)
        claim_id = resp.data['id']
        self.client.force_authenticate(user=self.author)
        resp = self.client.post(f'/api/v1/claims/{claim_id}/reject')
        self.assertEqual(resp.data['status'], 'rejected')
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'published')

    def test_cancel_releases_post(self):
        resp = self._claim(self.claimant)
        claim_id = resp.data['id']
        self.client.force_authenticate(user=self.claimant)
        resp = self.client.post(f'/api/v1/claims/{claim_id}/cancel')
        self.assertEqual(resp.data['status'], 'cancelled')
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'published')

    def test_contact_null_before_approved(self):
        resp = self._claim(self.claimant)
        claim_id = resp.data['id']
        self.client.force_authenticate(user=self.claimant)
        resp = self.client.get(f'/api/v1/claims/{claim_id}')
        self.assertIsNone(resp.data['contact'])

    def test_approve_then_both_confirm_handover(self):
        resp = self._claim(self.claimant)
        claim_id = resp.data['id']
        self.client.force_authenticate(user=self.author)
        resp = self.client.post(f'/api/v1/claims/{claim_id}/approve')
        self.assertEqual(resp.data['status'], 'approved')
        self.assertIsNotNone(resp.data['contact'])
        self.client.force_authenticate(user=self.claimant)
        resp = self.client.post(f'/api/v1/claims/{claim_id}/confirm-handover')
        self.assertEqual(resp.data['status'], 'approved')
        self.client.force_authenticate(user=self.author)
        resp = self.client.post(f'/api/v1/claims/{claim_id}/confirm-handover')
        self.assertEqual(resp.data['status'], 'completed')
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'completed')
