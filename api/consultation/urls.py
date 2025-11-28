from django.urls import path
from .views import (
    FarmerConsultationListCreateView,
    ConsultantConsultationDetailView,
    ConsultationAnswerCreateView,
)

urlpatterns = [
    # Petani
    path("farmer/consultations/", FarmerConsultationListCreateView.as_view(), name="farmer-consultations"),

    # Konsultan
    path("consultant/consultations/<int:pk>/", ConsultantConsultationDetailView.as_view(), name="consultation-detail"),
    path("consultant/consultations/<int:pk>/answer/", ConsultationAnswerCreateView.as_view(), name="consultation-answer"),
]
