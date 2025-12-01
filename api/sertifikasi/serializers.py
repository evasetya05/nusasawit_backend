from rest_framework import serializers
from .models import CertificationScheme


class CertificationSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationScheme
        fields = [
            "id",
            "name",
            "description",
        ]
