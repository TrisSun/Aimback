from rest_framework import serializers

from apps.posts.serializers import PostPublicSerializer

from . import constants
from .models import MatchCandidate


class MatchSearchSerializer(serializers.Serializer):
    source_post_id = serializers.IntegerField(required=False)
    target_type = serializers.ChoiceField(
        choices=["lost", "found"], required=False, allow_blank=True
    )
    text = serializers.CharField(required=False, allow_blank=True, default="")
    image_cos_key = serializers.CharField(required=False, allow_blank=True, default="")
    category_l1 = serializers.CharField(required=False, allow_blank=True)
    region_code = serializers.CharField(required=False, allow_blank=True)
    place_id = serializers.IntegerField(required=False, allow_null=True)
    event_start = serializers.DateTimeField(required=False)
    event_end = serializers.DateTimeField(required=False)
    q = serializers.CharField(required=False, allow_blank=True, default="")
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, default=20)

    def validate_page_size(self, value: int) -> int:
        return min(value, 50)

    def validate(self, attrs: dict) -> dict:
        if not attrs.get("source_post_id") and not attrs.get("target_type"):
            raise serializers.ValidationError(
                {"target_type": "无源帖时必须指定 target_type"}
            )
        event_start = attrs.get("event_start")
        event_end = attrs.get("event_end")
        if event_start and event_end and event_start > event_end:
            raise serializers.ValidationError(
                {"event_end": "结束时间不能早于开始时间"}
            )
        return attrs


class MatchFeedbackSerializer(serializers.Serializer):
    label = serializers.ChoiceField(
        choices=[constants.FEEDBACK_NOT_MATCH, "reset"]
    )


class MatchResultSerializer(serializers.Serializer):
    match_id = serializers.IntegerField()
    score = serializers.FloatField()
    vector_score = serializers.FloatField()
    reason = serializers.CharField()
    feedback = serializers.CharField(allow_blank=True)
    post = serializers.SerializerMethodField()

    def get_post(self, obj) -> dict:
        post = obj["post"] if isinstance(obj, dict) else obj
        return PostPublicSerializer(post).data


class SavedMatchSerializer(serializers.ModelSerializer):
    match_id = serializers.IntegerField(source="id")
    post = PostPublicSerializer(source="candidate_post")

    class Meta:
        model = MatchCandidate
        fields = [
            "match_id",
            "score",
            "vector_score",
            "reason",
            "feedback",
            "post",
        ]
