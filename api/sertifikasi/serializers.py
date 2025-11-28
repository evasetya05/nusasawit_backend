from rest_framework import serializers
from .models import CertificationScheme, CertificationProgress, CertificationTask


class CertificationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationTask
        fields = [
            "id",
            "title",
            "description",
            "planned_date",
            "status",
            "updated_at",
        ]


class CertificationProgressSerializer(serializers.ModelSerializer):
    scheme_name = serializers.CharField(source="scheme.name", read_only=True)
    farmer_name = serializers.CharField(source="farmer.username", read_only=True)
    tasks = CertificationTaskSerializer(many=True, read_only=True)

    class Meta:
        model = CertificationProgress
        fields = [
            "id",
            "scheme_name",
            "farmer_name",
            "status",
            "start_date",
            "completion_date",
            "tasks",
        ]
