from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.permission import HasValidAppKey
from apps.core.models import Employee
from apps.modules.compensation6.models import PayrollPeriod, WorkRequest

from .serializers import (
    EmployeeAvailabilitySerializer,
    EmployeeWorkCalendarSerializer,
    WorkRequestSummarySerializer,
)


class EmployeeAvailabilityView(APIView):
    permission_classes = [HasValidAppKey]

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


class EmployeeWorkCalendarView(APIView):
    permission_classes = [HasValidAppKey]

    def get(self, request):
        start_date_param = request.query_params.get("start_date")
        end_date_param = request.query_params.get("end_date")
        employee_param = request.query_params.get("employee")

        start_date = parse_date(start_date_param) if start_date_param else None
        if start_date_param and not start_date:
            return Response(
                {"detail": "Parameter start_date harus dalam format YYYY-MM-DD."},
                status=400,
            )

        end_date = parse_date(end_date_param) if end_date_param else None
        if end_date_param and not end_date:
            return Response(
                {"detail": "Parameter end_date harus dalam format YYYY-MM-DD."},
                status=400,
            )

        if start_date and not end_date:
            end_date = start_date
        if end_date and not start_date:
            start_date = end_date

        active_period = None
        if not start_date or not end_date:
            active_period = (
                PayrollPeriod.objects.filter(is_closed=False)
                .order_by("start_date")
                .first()
            )
            if not active_period:
                return Response(
                    {
                        "detail": (
                            "Tidak ada periode penggajian aktif dan parameter "
                            "start_date serta end_date wajib diisi."
                        )
                    },
                    status=400,
                )
            start_date = active_period.start_date
            end_date = active_period.end_date

        if start_date > end_date:
            return Response(
                {"detail": "start_date tidak boleh setelah end_date."},
                status=400,
            )

        date_span = (end_date - start_date).days
        if date_span > 90:
            return Response(
                {"detail": "Rentang tanggal maksimum 90 hari."},
                status=400,
            )

        employees_qs = (
            Employee.objects.filter(is_active=True)
            .prefetch_related("borongan")
            .order_by("name")
        )
        if employee_param:
            employees_qs = employees_qs.filter(pk=employee_param)

        employees = list(employees_qs)

        date_range = [
            start_date + timedelta(days=offset) for offset in range(date_span + 1)
        ]

        work_requests = (
            WorkRequest.objects.filter(
                employee__in=employees,
                start_date__lte=end_date,
                end_date__gte=start_date,
            )
            .select_related("employee")
            .order_by("employee__name", "start_date")
        )

        request_lookup = {}
        for wr in work_requests:
            wr_start = max(wr.start_date, start_date)
            wr_end = min(wr.end_date, end_date)
            current = wr_start
            while current <= wr_end:
                request_lookup[(wr.employee_id, current)] = wr
                current += timedelta(days=1)

        calendar_map = {employee.id: [] for employee in employees}
        for employee in employees:
            entries = calendar_map[employee.id]
            for current_date in date_range:
                wr = request_lookup.get((employee.id, current_date))
                entries.append(
                    {
                        "date": current_date,
                        "is_working": wr is not None,
                        "work_request": wr,
                    }
                )

        serializer = EmployeeWorkCalendarSerializer(
            employees,
            many=True,
            context={"calendar_map": calendar_map},
        )

        return Response(
            {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "date_range": [current.isoformat() for current in date_range],
                "employees": serializer.data,
            }
        )


class WorkRequestCreateView(APIView):
    """Create WorkRequest with user tracking."""
    permission_classes = [HasValidAppKey]

    def post(self, request):
        employee_id = request.data.get("employee_id")
        title = request.data.get("title")
        description = request.data.get("description", "")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        due_date = request.data.get("due_date")

        # Validate required fields
        if not employee_id or not title:
            return Response(
                {"detail": "employee_id dan title wajib diisi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate employee exists
        try:
            employee = Employee.objects.get(id=employee_id, is_active=True)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee tidak ditemukan atau tidak aktif."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Parse dates
        start_date_parsed = parse_date(start_date) if start_date else None
        end_date_parsed = parse_date(end_date) if end_date else None
        due_date_parsed = parse_date(due_date) if due_date else None

        # Check for existing WorkRequest for same employee and date range
        existing = WorkRequest.objects.filter(
            employee=employee,
            start_date=start_date_parsed,
            end_date=end_date_parsed
        ).first()
        
        if existing:
            return Response(
                {
                    "detail": f"WorkRequest sudah ada untuk {employee.name} pada periode {start_date_parsed} hingga {end_date_parsed}.",
                    "existing_request": {
                        "id": existing.id,
                        "title": existing.title,
                        "start_date": existing.start_date,
                        "end_date": existing.end_date
                    }
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Create WorkRequest with user tracking
        work_request = WorkRequest.objects.create(
            employee=employee,
            title=title,
            description=description,
            start_date=start_date_parsed,
            end_date=end_date_parsed,
            due_date=due_date_parsed,
            flutter_user=getattr(request, 'flutter_user', None),
            created_by=request.user if request.user.is_authenticated else None,
        )

        identifier = getattr(request, 'flutter_user_identifier', None) or getattr(
            request, 'user_identifier', 'unknown'
        )

        # Return created work request
        serializer = WorkRequestSummarySerializer(work_request)
        return Response(
            {
                "detail": "WorkRequest berhasil dibuat.",
                "work_request": serializer.data,
                "flutter_user_identifier": identifier,
            },
            status=status.HTTP_201_CREATED,
        )