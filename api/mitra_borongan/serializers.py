from rest_framework import serializers

from apps.core.models import Employee
from apps.core.models.employee import Borongan


class BoronganSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borongan
        fields = ["id", "pekerjaan", "satuan", "harga_borongan"]


class EmployeeAvailabilitySerializer(serializers.ModelSerializer):
    borongan = BoronganSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ["id", "name", "borongan", "is_available"]

    def get_is_available(self, obj):
        busy_employee_ids = self.context.get("busy_employee_ids", set())
        return obj.id not in busy_employee_ids
from rest_framework import serializers

from apps.core.models import Employee
from apps.core.models.employee import Borongan


class BoronganSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borongan
        fields = ["id", "pekerjaan", "satuan", "harga_borongan"]


class EmployeeAvailabilitySerializer(serializers.ModelSerializer):
    borongan = BoronganSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ["id", "name", "borongan", "is_available"]

    def get_is_available(self, obj):
        busy_employee_ids = self.context.get("busy_employee_ids", set())
        return obj.id not in busy_employee_ids