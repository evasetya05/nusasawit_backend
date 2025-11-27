from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Employee
from apps.core.models.employee import Borongan
from apps.modules.compensation6.models import WorkRequest

from .serializers import EmployeeAvailabilitySerializer


class EmployeeAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query_date = request.query_params.get("date")
        if query_date:
            target_date = parse_date(query_date)
            if not target_date:
                return Response(
                    {"detail": "Parameter date harus dalam format YYYY-MM-DD."},
                    status=400,
                )
        else:
            target_date = timezone.localdate()

        employees = (
            Employee.objects.filter(is_active=True)
            .prefetch_related("borongan")
            .order_by("name")
        )

        busy_employee_ids = set(
            WorkRequest.objects.filter(
                start_date__lte=target_date,
                end_date__gte=target_date,
            ).values_list("employee_id", flat=True)
        )

        serializer = EmployeeAvailabilitySerializer(
            employees,
            many=True,
            context={"busy_employee_ids": busy_employee_ids},
        )
        return Response({"date": target_date, "employees": serializer.data})