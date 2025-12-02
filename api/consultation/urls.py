from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsultantViewSet, ConsultationViewSet

router = DefaultRouter()
router.register(r'consultants', ConsultantViewSet, basename='consultant')
router.register(r'consultations', ConsultationViewSet, basename='consultation')

urlpatterns = [
    path('', include(router.urls)),
]