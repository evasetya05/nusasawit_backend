from urllib.parse import urljoin

from django.conf import settings
from rest_framework import serializers

from apps.core.models import Employee
from apps.core.models.employee import Borongan
from apps.modules.compensation6.models import WorkRequest
from apps.modules.area.models import Desa


class BoronganSerializer(serializers.ModelSerializer):
    employee_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = Borongan
        fields = ["id", "pekerjaan", "satuan", "harga_borongan", "employee_photo"]
    
    def get_employee_photo(self, obj):
        photo_field = getattr(obj.employee, "photo", None)
        if not photo_field:
            return None

        photo_name = getattr(photo_field, "name", "")
        if not photo_name:
            return None

        storage = getattr(photo_field, "storage", None)
        if storage and not storage.exists(photo_name):
            return None

        try:
            url = photo_field.url
        except ValueError:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(url)

        if url.startswith("http"):
            return url

        return urljoin(settings.MEDIA_URL, url.lstrip("/"))


class WorkRequestSummarySerializer(serializers.ModelSerializer):
    flutter_user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkRequest
        fields = ["id", "title", "description", "start_date", "end_date", "due_date", "flutter_user_info"]
    
    def get_flutter_user_info(self, obj):
        if obj.flutter_user:
            return {
                "identifier": obj.flutter_user.identifier,
                "email": obj.flutter_user.email,
                "phone_number": obj.flutter_user.phone_number,
            }
        return None


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desa
        fields = ["id", "nama", "jenis", "kode_pos", "alamat_lengkap"]
        depth = 2


class EmployeeAvailabilitySerializer(serializers.ModelSerializer):
    borongan = BoronganSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()
    area = AreaSerializer(source='desa', read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "name", "borongan", "is_available", "area"]

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