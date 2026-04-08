from rest_framework import serializers
from .models import Tip, TipContributor, TipDiscussion


class TipSerializer(serializers.ModelSerializer):
    contributor_name = serializers.CharField(source='contributor.name', read_only=True)
    consultant_name = serializers.CharField(source='contributor.consultant_name', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Tip
        fields = [
            'id',
            'title',
            'content',
            'category',
            'image_url',
            'contributor',
            'contributor_name',
            'consultant_name',
            'discussion',
            'created_at'
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image_url:
            if request is not None:
                return request.build_absolute_uri(obj.image_url.url)
            return obj.image_url.url
        return None

class TipContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipContributor
        fields = '__all__'


class TipDiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipDiscussion
        fields = ['id', 'tip', 'user_identifier', 'message', 'created_at']
