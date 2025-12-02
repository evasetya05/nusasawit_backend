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

    def get_queryset(self):
        """
        Filter konsultasi berdasarkan pengguna (petani) yang diidentifikasi
        melalui header X-EMAIL.
        """
        email = self.request.headers.get('X-EMAIL')
        if email:
            farmer = FlutterUser.objects.filter(email=email).first()
            if farmer:
                return Consultation.objects.filter(farmer=farmer)
        return Consultation.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultationListSerializer
        return ConsultationSerializer

    def perform_create(self, serializer):
        email = self.request.headers.get('X-EMAIL')
        phone = self.request.headers.get('X-PHONE')

        # Dapatkan pengguna Flutter pertama yang cocok dengan email, atau buat yang baru jika tidak ada.
        # Ini mencegah error 'MultipleObjectsReturned'.
        farmer = FlutterUser.objects.filter(email=email).first()
        if not farmer:
            farmer = FlutterUser.objects.create(
                email=email,
                defaults={'phone': phone, 'identifier': email}
            )

        serializer.save(farmer=farmer)


class ConsultationMessageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and creating consultation messages within a consultation.
    """
    queryset = ConsultationMessage.objects.all()
    serializer_class = ConsultationMessageSerializer
    permission_classes = [HasValidAppKey]

    def get_queryset(self):
        """
        Filter messages to only those belonging to the specified consultation,
        and ensure the requestor owns the consultation.
        """
        email = self.request.headers.get('X-EMAIL')
        consultation_pk = self.kwargs.get('consultation_pk')

        if email:
            farmer = FlutterUser.objects.filter(email=email).first()
            if farmer:
                # Filter pesan yang konsultasinya dimiliki oleh farmer yang melakukan request
                return self.queryset.filter(consultation_id=consultation_pk, consultation__farmer=farmer)
        return self.queryset.none()

    def perform_create(self, serializer):
        """
        Associate the message with the correct consultation from the URL
        and the sender from the request headers.
        """
        consultation = Consultation.objects.get(pk=self.kwargs['consultation_pk'])
        email = self.request.headers.get('X-EMAIL')
        farmer = FlutterUser.objects.filter(email=email).first()

        # Set sender based on who is making the request
        serializer.save(consultation=consultation, sender_farmer=farmer)