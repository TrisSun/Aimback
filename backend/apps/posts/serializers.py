from rest_framework import serializers

from . import constants
from .models import Place, Post, PostAttribute, PostImage, Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["code", "name"]


class PlacePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ["id", "name", "place_type"]


class PostImagePublicSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ["id", "sort_order", "review_status", "url"]

    def get_url(self, obj: PostImage) -> str | None:
        # 图片访问链接统一由 B 的 COS 签名凭证服务生成，A 不在帖子接口内拼接路径。
        # 联调接入 B 的服务后替换此占位实现。
        return None


class PostAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostAttribute
        fields = [
            "brand",
            "primary_color",
            "text_mark",
            "distinctive_features",
            "normalized_description",
        ]


class PostPublicSerializer(serializers.ModelSerializer):
    category_l1_label = serializers.SerializerMethodField()
    category_l2_label = serializers.SerializerMethodField()
    found_region = RegionSerializer(read_only=True)
    found_place = PlacePublicSerializer(read_only=True)
    images = PostImagePublicSerializer(many=True, read_only=True)
    attribute = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "type",
            "status",
            "category_l1",
            "category_l2",
            "category_l1_label",
            "category_l2_label",
            "title",
            "description",
            "found_region",
            "found_place",
            "custody_type",
            "event_start_at",
            "event_end_at",
            "published_at",
            "created_at",
            "updated_at",
            "images",
            "attribute",
        ]

    def get_category_l1_label(self, obj: Post) -> str:
        return constants.CATEGORY_L1_LABELS.get(obj.category_l1, obj.category_l1)

    def get_category_l2_label(self, obj: Post) -> str:
        return constants.CATEGORY_L2_LABELS.get(obj.category_l2, obj.category_l2)

    def get_attribute(self, obj: Post) -> dict | None:
        try:
            attribute = obj.attribute
        except AttributeError:
            return None
        return PostAttributeSerializer(attribute).data


class PostImageWriteSerializer(serializers.Serializer):
    cos_key = serializers.CharField(max_length=512)
    sort_order = serializers.IntegerField(min_value=0, default=0)


class PostWriteSerializer(serializers.ModelSerializer):
    found_region_code = serializers.SlugRelatedField(
        source="found_region",
        slug_field="code",
        queryset=Region.objects.all(),
        write_only=True,
    )
    found_place_id = serializers.PrimaryKeyRelatedField(
        source="found_place",
        queryset=Place.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    custody_place_id = serializers.PrimaryKeyRelatedField(
        source="custody_place",
        queryset=Place.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    images = PostImageWriteSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Post
        fields = [
            "type",
            "category_l1",
            "category_l2",
            "title",
            "description",
            "found_region_code",
            "found_place_id",
            "found_location_lat",
            "found_location_lng",
            "custody_type",
            "custody_place_id",
            "custody_address",
            "event_start_at",
            "event_end_at",
            "images",
        ]

    def validate(self, attrs: dict) -> dict:
        category_l1 = attrs.get("category_l1")
        category_l2 = attrs.get("category_l2")
        if category_l1 and category_l2 and not constants.is_valid_category(
            category_l1, category_l2
        ):
            raise serializers.ValidationError(
                {"category_l2": "二级分类与一级分类不匹配"}
            )

        event_start = attrs.get("event_start_at")
        event_end = attrs.get("event_end_at")
        if event_start and event_end and event_start > event_end:
            raise serializers.ValidationError(
                {"event_end_at": "结束时间不能早于开始时间"}
            )

        images = attrs.get("images", [])
        if len(images) > 4:
            raise serializers.ValidationError({"images": "最多上传 4 张图片"})

        return attrs

    def create(self, validated_data: dict) -> Post:
        images = validated_data.pop("images", [])
        post = Post.objects.create(**validated_data)
        self._replace_images(post, images)
        return post

    def update(self, instance: Post, validated_data: dict) -> Post:
        images = validated_data.pop("images", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images is not None:
            self._replace_images(instance, images)
        return instance

    @staticmethod
    def _replace_images(post: Post, images: list[dict]) -> None:
        post.images.all().delete()
        PostImage.objects.bulk_create(
            [
                PostImage(
                    post=post,
                    cos_key=item["cos_key"],
                    sort_order=item.get("sort_order", 0),
                )
                for item in images
            ]
        )
