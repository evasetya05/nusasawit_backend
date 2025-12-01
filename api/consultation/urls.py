from django.urls import path

from .views import (
    FarmerConsultationListCreateView,
    ConsultantConsultationDetailView,
    ConsultationMessageListCreateView,
    ConsultantListView,
    ConsultantAssignView,
    ConsultationAnswerCreateView,
)

urlpatterns = [
    # Petani
    path("farmer/consultations/", FarmerConsultationListCreateView.as_view(), name="farmer-consultations"),

    # Konsultan
    path("consultant/consultations/<int:pk>/", ConsultantConsultationDetailView.as_view(), name="consultation-detail"),
    path("consultant/consultations/<int:pk>/messages/", ConsultationMessageListCreateView.as_view(), name="consultation-messages"),
    path("consultant/consultations/<int:pk>/assign/", ConsultantAssignView.as_view(), name="consultation-assign"),
    
    # Daftar Konsultan
    path("consultants/", ConsultantListView.as_view(), name="consultant-list"),

    # Backward compatibility
    path("consultant/consultations/<int:pk>/answer/", ConsultationAnswerCreateView.as_view(), name="consultation-answer"),
]
