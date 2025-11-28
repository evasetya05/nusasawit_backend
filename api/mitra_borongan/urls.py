from django.urls import path

from .views import EmployeeAvailabilityView, EmployeeWorkCalendarView

app_name = "mitra"

urlpatterns = [
    path("", EmployeeAvailabilityView.as_view(), name="employee_availability"),
    path("calendar/", EmployeeWorkCalendarView.as_view(), name="employee_work_calendar"),
]