from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .filters import apply_post_hard_filters, apply_post_search_query
from .models import Place, Post, PostAttribute, Region
from .serializers import PostAttributeSerializer, PostPublicSerializer

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

    def test_search_query_matches_title_description_and_attribute(self):
        post = self._create_post(title="iPhone 14", description="黑色手机")
        PostAttribute.objects.create(
            post=post,
            brand="Apple",
            primary_color="black",
            text_mark="A",
            distinctive_features="无",
            normalized_description="黑色手机",
        )

        self.assertEqual(
            apply_post_search_query(Post.objects.all(), "iPhone").count(), 1
        )
        self.assertEqual(
            apply_post_search_query(Post.objects.all(), "黑色").count(), 1
        )
        self.assertEqual(
            apply_post_search_query(Post.objects.all(), "Apple").count(), 1
        )
        self.assertEqual(
            apply_post_search_query(Post.objects.all(), "不存在").count(), 0
        )

    def test_primary_color_enum_validation(self):
        serializer = PostAttributeSerializer(
            data={
                "brand": "Apple",
                "primary_color": "redish",
                "text_mark": "",
                "distinctive_features": "",
                "normalized_description": "",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("primary_color", serializer.errors)


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

    def _create_post(self, author=None, **overrides):
        data = {
            "author": author or self.user,
            "type": "found",
            "status": "published",
            "category_l1": "electronics",
            "category_l2": "phone",
            "title": None,
            "description": "图书馆三楼捡到手机",
            "found_region": self.region,
            "found_place": self.place,
            "event_start_at": self.now - timedelta(hours=1),
            "event_end_at": self.now,
            "published_at": self.now,
        }
        data.update(overrides)
        return Post.objects.create(**data)

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
        post = self._create_post(status="draft")
        self.client.force_authenticate(self.other)
        resp = self.client.get(f"/api/v1/posts/{post.id}")
        self.assertEqual(resp.status_code, 403)

        self.client.force_authenticate(self.user)
        resp = self.client.get(f"/api/v1/posts/{post.id}")
        self.assertEqual(resp.status_code, 200)

    def test_create_requires_custody_place_for_official(self):
        self.client.force_authenticate(self.user)
        payload = dict(self.payload, custody_type="official", custody_place_id=None)
        resp = self.client.post("/api/v1/posts", payload, format="json")
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("custody_place_id", resp.data)

    def test_create_rejects_future_event_end(self):
        self.client.force_authenticate(self.user)
        payload = dict(self.payload)
        payload["event_end_at"] = (self.now + timedelta(days=1)).isoformat()
        resp = self.client.post("/api/v1/posts", payload, format="json")
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("event_end_at", resp.data)

    def test_create_requires_custody_type(self):
        self.client.force_authenticate(self.user)
        payload = dict(self.payload)
        payload.pop("custody_type")
        resp = self.client.post("/api/v1/posts", payload, format="json")
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("custody_type", resp.data)

    def test_create_rejects_lat_out_of_range(self):
        self.client.force_authenticate(self.user)
        payload = dict(self.payload, found_location_lat="91.000000")
        resp = self.client.post("/api/v1/posts", payload, format="json")
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("found_location_lat", resp.data)

    def test_create_rejects_lng_out_of_range(self):
        self.client.force_authenticate(self.user)
        payload = dict(self.payload, found_location_lng="181.000000")
        resp = self.client.post("/api/v1/posts", payload, format="json")
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertIn("found_location_lng", resp.data)

    def test_publish_non_draft_returns_conflict(self):
        post = self._create_post(status="published")
        self.client.force_authenticate(self.user)
        resp = self.client.post(f"/api/v1/posts/{post.id}/publish")
        self.assertEqual(resp.status_code, 409)

    def test_close_state_transitions(self):
        self.client.force_authenticate(self.user)

        completed = self._create_post(status="completed")
        resp = self.client.post(f"/api/v1/posts/{completed.id}/close")
        self.assertEqual(resp.status_code, 409)

        closed = self._create_post(status="closed")
        resp = self.client.post(f"/api/v1/posts/{closed.id}/close")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "closed")

        published = self._create_post(status="published")
        resp = self.client.post(f"/api/v1/posts/{published.id}/close")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "closed")

    def test_patch_terminal_state_returns_conflict(self):
        post = self._create_post(status="closed")
        self.client.force_authenticate(self.user)
        resp = self.client.patch(
            f"/api/v1/posts/{post.id}", {"title": "新标题"}, format="json"
        )
        self.assertEqual(resp.status_code, 409)

    def test_delete_only_allows_draft_or_closed(self):
        self.client.force_authenticate(self.user)

        draft = self._create_post(status="draft")
        resp = self.client.delete(f"/api/v1/posts/{draft.id}")
        self.assertEqual(resp.status_code, 204)

        closed = self._create_post(status="closed")
        resp = self.client.delete(f"/api/v1/posts/{closed.id}")
        self.assertEqual(resp.status_code, 204)

        published = self._create_post(status="published")
        resp = self.client.delete(f"/api/v1/posts/{published.id}")
        self.assertEqual(resp.status_code, 409)

        others_draft = self._create_post(author=self.other, status="draft")
        resp = self.client.delete(f"/api/v1/posts/{others_draft.id}")
        self.assertEqual(resp.status_code, 403)

    def test_list_q_and_default_sort(self):
        post = self._create_post(
            title="iPhone", description="黑色", published_at=self.now
        )
        PostAttribute.objects.create(
            post=post,
            brand="Apple",
            primary_color="black",
            text_mark="",
            distinctive_features="",
            normalized_description="",
        )
        older = self._create_post(
            title="钱包", published_at=self.now - timedelta(hours=1)
        )

        self.client.force_authenticate(self.user)
        resp = self.client.get("/api/v1/posts", {"q": "Apple"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["id"], post.id)

        resp = self.client.get("/api/v1/posts")
        ids = [item["id"] for item in resp.data["results"]]
        self.assertEqual(ids, [post.id, older.id])

    def test_list_does_not_hard_filter_by_category_l2(self):
        self._create_post(
            category_l2="phone", published_at=self.now
        )
        self._create_post(
            category_l2="laptop", published_at=self.now
        )

        self.client.force_authenticate(self.user)
        resp = self.client.get("/api/v1/posts", {"category_l2": "phone"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)
