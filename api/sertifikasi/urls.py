from django.urls import path
from .views import (
    FlutterCertificationListView,
)

urlpatterns = [
    path("flutter/certifications/", FlutterCertificationListView.as_view(),
         name="flutter-certification-list"),
]
