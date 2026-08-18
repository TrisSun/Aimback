from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .filters import apply_post_hard_filters
from .models import Place, Post, Region
from .serializers import PostPublicSerializer

User = get_user_model()


class PostModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="a", password="pass")
        self.region = Region.objects.create(
            code="440305", name="南山区", level="district"
        )
        self.place = Place.objects.create(
            name="图书馆", region=self.region, place_type="school"
        )
        self.now = timezone.now()

    def _create_post(self, **overrides):
        data = {
            "author": self.user,
            "type": "found",
            "status": "published",
            "category_l1": "electronics",
            "category_l2": "phone",
            "description": "图书馆三楼捡到手机",
            "found_region": self.region,
            "found_place": self.place,
            "event_start_at": self.now - timedelta(hours=1),
            "event_end_at": self.now,
        }
        data.update(overrides)
        return Post.objects.create(**data)

    def test_hard_filters_only_return_searchable_statuses(self):
        self._create_post(status="published")
        self._create_post(status="draft")
        self._create_post(status="completed")
        self._create_post(status="closed")

        qs = apply_post_hard_filters(Post.objects.all())
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().status, "published")

    def test_hard_filters_type_and_category(self):
        self._create_post(type="lost")
        self._create_post(type="found", category_l1="other", category_l2="other")
        self._create_post(type="found", category_l1="bags", category_l2="wallet")

        qs = apply_post_hard_filters(Post.objects.all(), type="found")
        self.assertEqual(qs.count(), 2)

        qs = apply_post_hard_filters(
            Post.objects.all(), category_l1="electronics"
        )
        self.assertEqual(qs.count(), 1)

        qs = apply_post_hard_filters(Post.objects.all(), category_l1="other")
        self.assertEqual(qs.count(), 3)

    def test_hard_filters_region_place_and_time_window(self):
        region_b = Region.objects.create(code="440300", name="深圳市", level="city")
        self._create_post()
        self._create_post(found_region=region_b, found_place=None)

        qs = apply_post_hard_filters(Post.objects.all(), region_code="440305")
        self.assertEqual(qs.count(), 1)

        qs = apply_post_hard_filters(Post.objects.all(), place_id=self.place.id)
        self.assertEqual(qs.count(), 1)

        qs = apply_post_hard_filters(
            Post.objects.all(),
            event_start=self.now + timedelta(days=1),
            event_end=self.now + timedelta(days=2),
        )
        self.assertEqual(qs.count(), 0)

    def test_public_serializer_does_not_leak_sensitive_fields(self):
        post = self._create_post(
            found_location_lat="22.533300",
            found_location_lng="113.930000",
            custody_type="official",
            custody_address="校内保卫处",
        )
        data = PostPublicSerializer(post).data

        self.assertNotIn("found_location_lat", data)
        self.assertNotIn("found_location_lng", data)
        self.assertNotIn("custody_address", data)
        self.assertNotIn("author", data)


class PostApiTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="a", password="pass")
        self.other = User.objects.create_user(username="b", password="pass")
        self.region = Region.objects.create(
            code="440305", name="南山区", level="district"
        )
        self.place = Place.objects.create(
            name="图书馆", region=self.region, place_type="school"
        )
        self.client = APIClient()
        self.now = timezone.now()
        self.payload = {
            "type": "found",
            "category_l1": "electronics",
            "category_l2": "phone",
            "title": None,
            "description": "图书馆三楼捡到手机",
            "found_region_code": "440305",
            "found_place_id": self.place.id,
            "found_location_lat": "22.533300",
            "found_location_lng": "113.930000",
            "custody_type": "personal",
            "custody_place_id": None,
            "custody_address": "",
            "event_start_at": (self.now - timedelta(hours=1)).isoformat(),
            "event_end_at": self.now.isoformat(),
            "images": [{"cos_key": "posts/uuid.jpg", "sort_order": 0}],
        }

    def test_create_publish_and_list_flow(self):
        self.client.force_authenticate(self.user)
        create_resp = self.client.post("/api/v1/posts", self.payload, format="json")
        self.assertEqual(create_resp.status_code, 201, create_resp.content)
        post_id = create_resp.data["id"]
        self.assertEqual(create_resp.data["status"], "draft")
        self.assertNotIn("found_location_lat", create_resp.data)

        list_resp = self.client.get("/api/v1/posts")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(list_resp.data["count"], 0)
        self.assertIn("page", list_resp.data)
        self.assertIn("page_size", list_resp.data)
        self.assertIn("results", list_resp.data)

        publish_resp = self.client.post(f"/api/v1/posts/{post_id}/publish")
        self.assertEqual(publish_resp.status_code, 200, publish_resp.content)
        self.assertEqual(publish_resp.data["status"], "published")

        list_resp = self.client.get("/api/v1/posts")
        self.assertEqual(list_resp.data["count"], 1)
        self.assertIn("page", list_resp.data)
        self.assertIn("page_size", list_resp.data)
        self.assertIn("results", list_resp.data)

    def test_draft_detail_requires_author(self):
        post = Post.objects.create(
            author=self.user,
            type="found",
            status="draft",
            category_l1="electronics",
            category_l2="phone",
            description="草稿",
            found_region=self.region,
            event_start_at=self.now,
            event_end_at=self.now,
        )
        self.client.force_authenticate(self.other)
        resp = self.client.get(f"/api/v1/posts/{post.id}")
        self.assertEqual(resp.status_code, 403)

        self.client.force_authenticate(self.user)
        resp = self.client.get(f"/api/v1/posts/{post.id}")
        self.assertEqual(resp.status_code, 200)
