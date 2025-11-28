from rest_framework import serializers
from .models import Consultation, ConsultationAnswer


class ConsultationAnswerSerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(source="consultant.username", read_only=True)

    class Meta:
        model = ConsultationAnswer
        fields = ["id", "answer", "consultant_name", "answered_at"]


class ConsultationSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source="farmer.username", read_only=True)
    answer = ConsultationAnswerSerializer(read_only=True)

    class Meta:
        model = Consultation
        fields = [
            "id",
            "farmer_name",
            "question",
            "status",
            "answer",
            "created_at",
        ]
