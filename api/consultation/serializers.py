from rest_framework import serializers
from .models import Consultant, Consultation, ConsultationMessage
from api.user_flutter.models import FlutterUser


class ConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = ['id', 'name', 'profile_picture', 'institution_name', 'bio']


class ConsultationMessageSerializer(serializers.ModelSerializer):
    sender_farmer_id = serializers.PrimaryKeyRelatedField(
        source='sender_farmer', read_only=True
    )
    sender_consultant_id = serializers.PrimaryKeyRelatedField(
        source='sender_consultant', read_only=True
    )

    class Meta:
        model = ConsultationMessage
        fields = [
            'id', 'consultation', 'sender_farmer_id', 'sender_consultant_id', 
            'content', 'image', 'created_at'
        ]
        read_only_fields = ['created_at', 'consultation']


class ConsultationSerializer(serializers.ModelSerializer):
    messages = ConsultationMessageSerializer(many=True, read_only=True)
    farmer_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source='farmer'
    )
    consultant_id = serializers.PrimaryKeyRelatedField(
        queryset=Consultant.objects.all(), source='consultant', write_only=True
    )

    class Meta:
        model = Consultation
        fields = [
            'id', 'farmer_id', 'consultant_id', 'topic', 'status', 
            'created_at', 'updated_at', 'messages'
        ]
        read_only_fields = ['created_at', 'updated_at', 'messages', 'status']


class ConsultationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ['id', 'topic', 'status', 'created_at']