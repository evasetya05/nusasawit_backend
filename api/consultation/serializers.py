from rest_framework import serializers
from apps.core.models import Consultant
from .models import Consultation, ConsultationMessage
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
    sender_type = serializers.SerializerMethodField()
    sender_label = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationMessage
        fields = [
            'id',
            'consultation',
            'content',
            'image',
            'sender_farmer_id',
            'sender_consultant_id',
            'sender_type',
            'sender_label',
            'sender_name',
            'created_at'
        ]
        read_only_fields = ['created_at', 'consultation']

    def get_sender_type(self, obj):
        if obj.sender_consultant_id:
            return 'consultant'
        if obj.sender_farmer_id:
            return 'farmer'
        return 'system'

    def get_sender_label(self, obj):
        if obj.sender_consultant_id:
            name = obj.sender_consultant.name or getattr(obj.sender_consultant.user, 'get_full_name', lambda: None)()
            return f"Konsultan · {name or 'N/A'}"
        if obj.sender_farmer_id:
            return f"Flutter User · {obj.sender_farmer.identifier}"
        return 'Sistem'

    def get_sender_name(self, obj):
        if obj.sender_consultant_id:
            return obj.sender_consultant.name or getattr(obj.sender_consultant.user, 'username', None)
        if obj.sender_farmer_id:
            return obj.sender_farmer.identifier
        return 'System'


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