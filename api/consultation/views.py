from rest_framework import viewsets, permissions
from .models import Consultant, Consultation, ConsultationMessage
from api.permission import HasValidAppKey
from api.user_flutter.models import FlutterUser
from .serializers import (
    ConsultantSerializer, 
    ConsultationSerializer, 
    ConsultationMessageSerializer,
    ConsultationListSerializer
)

class ConsultantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing consultants.
    """
    queryset = Consultant.objects.all()
    serializer_class = ConsultantSerializer
    permission_classes = [HasValidAppKey]


class ConsultationViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing consultations.
    """
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [HasValidAppKey]

    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultationListSerializer
        return ConsultationSerializer

    def perform_create(self, serializer):
        email = self.request.headers.get('X-EMAIL')
        phone = self.request.headers.get('X-PHONE')

        # Dapatkan atau buat pengguna Flutter berdasarkan email dan telepon
        farmer, created = FlutterUser.objects.get_or_create(
            email=email,
            defaults={'phone': phone, 'identifier': email}
        )

        serializer.save(farmer=farmer)