from django.urls import path
from .views import (
    FlutterCertificationListView,
    FlutterCertificationDetailView,
)

urlpatterns = [
    path("flutter/certifications/", FlutterCertificationListView.as_view(),
         name="flutter-certification-list"),
    path("flutter/certifications/<int:pk>/", FlutterCertificationDetailView.as_view(),
         name="flutter-certification-detail"),
]
