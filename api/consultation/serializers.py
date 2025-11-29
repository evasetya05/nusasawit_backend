from rest_framework import serializers
from .models import Consultation, ConsultationAnswer


class ConsultationAnswerSerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(source="consultant.username", read_only=True)

    class Meta:
        model = ConsultationAnswer
        fields = ["id", "answer", "consultant_name", "institution_name", "answered_at"]


class ConsultationSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source="farmer.username", read_only=True)
    answer = ConsultationAnswerSerializer(read_only=True)
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    def get_email(self, obj):
        # Get email from request headers if available
        request = self.context.get('request')
        if request:
            return request.headers.get('X-EMAIL')
        return None

    def get_phone(self, obj):
        # Get phone from request headers if available
        request = self.context.get('request')
        if request:
            return request.headers.get('X-PHONE')
        return None
        
    def create(self, validated_data):
        # Set the farmer to the current user from the request
        request = self.context.get('request')
        if request and hasattr(request, 'flutter_user'):
            validated_data['farmer'] = request.flutter_user
        return super().create(validated_data)

    class Meta:
        model = Consultation
        fields = [
            "id",
            "farmer_name",
            "email",
            "phone",
            "question",
            "status",
            "answer",
            "created_at",
        ]
