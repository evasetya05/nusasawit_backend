from django.urls import path

from .views import EmployeeAvailabilityView

app_name = "mitra"

urlpatterns = [
    path("", EmployeeAvailabilityView.as_view(), name="employee_availability"),
]