from rest_framework import serializers
from .models import Tip, TipContributor, TipDiscussion


class TipContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipContributor
        fields = '__all__'

class TipSerializer(serializers.ModelSerializer):
    contributor_name = serializers.CharField(source='contributor.name', read_only=True)
    consultant_name = serializers.CharField(source='contributor.consultant_name', read_only=True)
    
    class Meta:
        model = Tip
        fields = ['id', 'title', 'content', 'category', 'image_url', 'contributor', 'contributor_name', 'consultant_name', 'discussion', 'created_at']


class TipDiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipDiscussion
        fields = ['id', 'tip', 'user_identifier', 'message', 'created_at']
