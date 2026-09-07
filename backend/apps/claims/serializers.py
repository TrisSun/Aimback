from rest_framework import serializers

from .models import Claim, ClaimAnswer, ClaimQuestion


class ClaimQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimQuestion
        fields = ['id', 'question', 'sort_order']


class ClaimAnswerSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='question.question', read_only=True)

    class Meta:
        model = ClaimAnswer
        fields = ['question_id', 'question', 'answer']


class ClaimPublicSerializer(serializers.ModelSerializer):
    answers = ClaimAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Claim
        fields = [
            'id', 'post', 'claimant', 'status', 'answers',
            'author_confirmed', 'claimant_confirmed',
            'created_at', 'approved_at', 'completed_at',
        ]


class ClaimDetailSerializer(ClaimPublicSerializer):
    contact = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = [
            'id', 'post', 'claimant', 'status', 'answers',
            'author_confirmed', 'claimant_confirmed',
            'created_at', 'approved_at', 'completed_at',
            'contact',
        ]

    def get_contact(self, obj):
        if obj.status != 'approved':
            return None
        post = obj.post
        place = post.custody_place
        return {
            'post_author_phone': post.author.username,
            'claimant_phone': obj.claimant.username,
            'custody_place': (
                {'id': place.id, 'name': place.name, 'place_type': place.place_type, 'address': place.address}
                if place else None
            ),
            'custody_address': post.custody_address or None,
        }
