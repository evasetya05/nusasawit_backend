from django.urls import path
from .views import (
    FarmerCertificationListCreateView,
    CertificationProgressDetailView,
    CertificationTaskCreateView,
)

urlpatterns = [
    path("farmer/certifications/", FarmerCertificationListCreateView.as_view(),
         name="farmer-certifications"),
         
    path("certifications/<int:pk>/", CertificationProgressDetailView.as_view(),
         name="certification-detail"),
         
    path("certifications/<int:pk>/tasks/add/", CertificationTaskCreateView.as_view(),
         name="certification-task-add"),
]
