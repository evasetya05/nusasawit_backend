from django.urls import path
from .views import JobCreateView,JobUpdateView, JobDeleteView

app_name = "jobs"
urlpatterns = [
    path('create/', JobCreateView.as_view(), name="create-job"),
    path('update/<int:pk>', JobUpdateView.as_view(), name="update-job"),
    path('delete/<int:pk>', JobDeleteView.as_view(), name="delete-job"),
]
