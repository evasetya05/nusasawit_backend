from rest_framework import serializers
from django.conf import settings

from apps.core.models import Employee
from apps.core.models.employee import Borongan
from apps.modules.compensation6.models import WorkRequest


class BoronganSerializer(serializers.ModelSerializer):
    employee_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Borongan
        fields = ["id", "pekerjaan", "satuan", "harga_borongan", "employee_photo"]
    
    def get_employee_photo(self, obj):
        if obj.employee.photo:
            return f"{settings.MEDIA_URL}{obj.employee.photo}"
        return None


class WorkRequestSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkRequest
        fields = ["id", "title", "description", "start_date", "end_date", "due_date"]


class EmployeeAvailabilitySerializer(serializers.ModelSerializer):
    borongan = BoronganSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ["id", "name", "borongan", "is_available"]

    def get_is_available(self, obj):
        busy_employee_ids = self.context.get("busy_employee_ids", set())
        return obj.id not in busy_employee_ids


class EmployeeWorkCalendarSerializer(serializers.ModelSerializer):
    borongan = BoronganSerializer(many=True, read_only=True)
    calendar = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ["id", "name", "borongan", "calendar"]

    def get_calendar(self, obj):
        calendar_map = self.context.get("calendar_map", {})
        day_entries = calendar_map.get(obj.id, [])
        return [
            {
                "date": entry["date"].isoformat(),
                "is_working": entry["is_working"],
                "work_request": WorkRequestSummarySerializer(entry["work_request"]).data
                if entry["work_request"]
                else None,
            }
            for entry in day_entries
        ]