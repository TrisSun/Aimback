from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.ai import constants
from apps.ai.embed import process_pending, sync_post_embeddings
from apps.ai.models import ImageEmbedding
from apps.ai.vectors import cosine_score
from apps.posts.models import Place, Post, PostImage, Region

User = get_user_model()


def pad512(*values: float) -> list[float]:
    vector = [float(v) for v in values]
    if len(vector) < constants.EMBEDDING_DIM:
        vector.extend([0.0] * (constants.EMBEDDING_DIM - len(vector)))
    return vector[: constants.EMBEDDING_DIM]


@override_settings(AI_EMBEDDING_PROVIDER="fake", AI_EMBED_INLINE=False)
class AiMatchTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="13800000001", password="pass")
        self.other = User.objects.create_user(username="13800000002", password="pass")
        self.region = Region.objects.create(
            code="440305", name="南山区", level="district"
        )
        self.place = Place.objects.create(
            name="图书馆", region=self.region, place_type="school"
        )
        self.place_b = Place.objects.create(
            name="食堂", region=self.region, place_type="school"
        )
        self.now = timezone.now()
        self.client = APIClient()

    def _create_post(self, author=None, **overrides):
        data = {
            "author": author or self.user,
            "type": "found",
            "status": "published",
            "category_l1": "electronics",
            "category_l2": "phone",
            "title": "黑色手机",
            "description": "图书馆捡到一部手机",
            "found_region": self.region,
            "found_place": self.place,
            "event_start_at": self.now - timedelta(hours=2),
            "event_end_at": self.now - timedelta(hours=1),
            "published_at": self.now,
        }
        data.update(overrides)
        return Post.objects.create(**data)

    def _ready_vector(self, post: Post, values, image: PostImage | None = None):
        sync_post_embeddings(post)
        qs = ImageEmbedding.objects.filter(
            post=post, version=constants.EMBEDDING_VERSION
        )
        if image is not None:
            qs = qs.filter(post_image=image)
        else:
            qs = qs.filter(post_image__isnull=True)
        row = qs.get()
        row.vector = pad512(*values)
        row.status = constants.STATUS_READY
        row.error = ""
        row.save(update_fields=["vector", "status", "error", "updated_at"])
        return row

    def test_cosine_identical_vectors(self):
        left = pad512(1, 0, 0)
        self.assertAlmostEqual(cosine_score(left, left), 1.0, places=5)

    def test_search_requires_login(self):
        resp = self.client.post(
            "/api/v1/matches/search", {"target_type": "found"}, format="json"
        )
        self.assertIn(resp.status_code, (401, 403))

    def test_adhoc_requires_target_type(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post("/api/v1/matches/search", {}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("target_type", resp.data)

    def test_source_post_must_be_owner(self):
        lost = self._create_post(author=self.other, type="lost")
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_opposite_type_only(self):
        lost = self._create_post(type="lost", description="丢失黑色手机")
        found_phone = self._create_post(
            author=self.other, type="found", description="捡到黑色手机"
        )
        wrong_type = self._create_post(
            author=self.other, type="lost", description="也丢失黑色手机"
        )
        self._ready_vector(lost, (1, 0, 0))
        self._ready_vector(found_phone, (1, 0, 0))
        self._ready_vector(wrong_type, (1, 0, 0))

        self.client.force_authenticate(self.user)
        resp = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        ids = [item["post"]["id"] for item in resp.data["results"]]
        self.assertIn(found_phone.id, ids)
        self.assertNotIn(wrong_type.id, ids)
        self.assertNotIn(lost.id, ids)

    def test_multi_view_uses_max_cosine(self):
        lost = self._create_post(type="lost", description="丢失手机")
        found = self._create_post(
            author=self.other, type="found", description="捡到手机"
        )
        img_a = PostImage.objects.create(post=found, cos_key="a.jpg", sort_order=0)
        img_b = PostImage.objects.create(post=found, cos_key="b.jpg", sort_order=1)
        self._ready_vector(lost, (1, 0, 0))
        self._ready_vector(found, (0, 1, 0), image=img_a)
        self._ready_vector(found, (1, 0, 0), image=img_b)

        self.client.force_authenticate(self.user)
        resp = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.data["count"], 1)
        self.assertAlmostEqual(
            resp.data["results"][0]["vector_score"], 1.0, places=5
        )

    def test_keyword_union_includes_post_without_embedding(self):
        lost = self._create_post(type="lost", title="iPhone")
        found = self._create_post(
            author=self.other,
            type="found",
            title="iPhone 14",
            description="食堂捡到",
        )
        other = self._create_post(
            author=self.other,
            type="found",
            title="雨伞",
            description="另一件",
            category_l2="other_electronics",
        )
        self._ready_vector(lost, (1, 0, 0))
        self._ready_vector(other, (0, 1, 0))
        # found 没有 ready 向量，只能靠关键词进来
        sync_post_embeddings(found)

        self.client.force_authenticate(self.user)
        resp = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id, "q": "iPhone"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        ids = [item["post"]["id"] for item in resp.data["results"]]
        self.assertIn(found.id, ids)
        item = next(x for x in resp.data["results"] if x["post"]["id"] == found.id)
        self.assertIn("关键词命中", item["reason"])
        self.assertEqual(item["vector_score"], 0)

    def test_feedback_persists_across_search(self):
        lost = self._create_post(type="lost")
        found = self._create_post(author=self.other, type="found")
        self._ready_vector(lost, (1, 0, 0))
        self._ready_vector(found, (1, 0, 0))

        self.client.force_authenticate(self.user)
        first = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id},
            format="json",
        )
        self.assertEqual(first.status_code, 200, first.content)
        match_id = first.data["results"][0]["match_id"]
        fb = self.client.post(
            f"/api/v1/matches/{match_id}/feedback",
            {"label": "not_match"},
            format="json",
        )
        self.assertEqual(fb.status_code, 200)
        self.assertEqual(fb.data["feedback"], "not_match")

        second = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id},
            format="json",
        )
        self.assertEqual(second.data["results"][0]["match_id"], match_id)
        self.assertEqual(second.data["results"][0]["feedback"], "not_match")

        saved = self.client.get(f"/api/v1/posts/{lost.id}/matches")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.data["count"], 1)
        self.assertEqual(saved.data["results"][0]["feedback"], "not_match")

    def test_degrade_without_embeddings(self):
        lost = self._create_post(type="lost")
        found = self._create_post(author=self.other, type="found")
        sync_post_embeddings(lost)
        sync_post_embeddings(found)

        self.client.force_authenticate(self.user)
        resp = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        ids = [item["post"]["id"] for item in resp.data["results"]]
        self.assertEqual(ids, [found.id])
        self.assertEqual(resp.data["results"][0]["vector_score"], 0)

    def test_same_place_ranks_higher_when_vectors_equal(self):
        lost = self._create_post(type="lost", found_place=self.place)
        near = self._create_post(
            author=self.other, type="found", found_place=self.place
        )
        far = self._create_post(
            author=self.other, type="found", found_place=self.place_b
        )
        self._ready_vector(lost, (1, 0, 0))
        self._ready_vector(near, (1, 0, 0))
        self._ready_vector(far, (1, 0, 0))

        self.client.force_authenticate(self.user)
        resp = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        ids = [item["post"]["id"] for item in resp.data["results"]]
        self.assertEqual(ids[0], near.id)
        self.assertIn("同一场所", resp.data["results"][0]["reason"])

    def test_fake_provider_process_pending(self):
        post = self._create_post(description="捡到一部黑色手机")
        sync_post_embeddings(post)
        pending = ImageEmbedding.objects.filter(
            post=post, status=constants.STATUS_PENDING
        )
        self.assertEqual(pending.count(), 1)
        done = process_pending(limit=10, post_id=post.pk)
        self.assertEqual(done, 1)
        row = ImageEmbedding.objects.get(post=post)
        self.assertEqual(row.status, constants.STATUS_READY)
        self.assertEqual(len(row.vector), constants.EMBEDDING_DIM)

    def test_feedback_forbidden_for_others(self):
        lost = self._create_post(type="lost")
        found = self._create_post(author=self.other, type="found")
        self._ready_vector(lost, (1, 0, 0))
        self._ready_vector(found, (1, 0, 0))
        self.client.force_authenticate(self.user)
        resp = self.client.post(
            "/api/v1/matches/search",
            {"source_post_id": lost.id},
            format="json",
        )
        match_id = resp.data["results"][0]["match_id"]
        self.client.force_authenticate(self.other)
        denied = self.client.post(
            f"/api/v1/matches/{match_id}/feedback",
            {"label": "not_match"},
            format="json",
        )
        self.assertEqual(denied.status_code, 403)
