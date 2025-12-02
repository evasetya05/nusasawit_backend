from django.urls import path, include
from rest_framework_nested import routers
from .views import ConsultantViewSet, ConsultationViewSet, ConsultationMessageViewSet

# Router utama
router = routers.DefaultRouter()
router.register(r'consultants', ConsultantViewSet)
router.register(r'consultations', ConsultationViewSet)

# Router bersarang untuk messages di dalam consultations
consultations_router = routers.NestedDefaultRouter(router, r'consultations', lookup='consultation')
consultations_router.register(r'messages', ConsultationMessageViewSet, basename='consultation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(consultations_router.urls)),
]