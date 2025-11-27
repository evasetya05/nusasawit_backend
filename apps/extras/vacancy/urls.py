from django.urls import path
from .views import ApplyJobView, select_for_exam,cancel_for_exam, view_cv

app_name = "vacancy"
urlpatterns = [
    path('apply/<int:pk>', ApplyJobView.as_view(), name="apply"),
    path('interview/<int:application_id>', select_for_exam, name="exam"),
    path('cancle-exam/<int:application_id>', cancel_for_exam, name="cancel-exam"),
    path('view-cv/<int:application_id>', view_cv, name="view-cv")
]
