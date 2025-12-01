from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permission import HasValidAppKey

from .models import Consultation, ConsultationAnswer
from .serializers import ConsultationSerializer, ConsultationAnswerSerializer


class FarmerConsultationListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasValidAppKey]
    serializer_class = ConsultationSerializer

    def get_queryset(self):
        return Consultation.objects.filter(farmer=self.request.flutter_user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.flutter_user)


class ConsultantConsultationDetailView(generics.RetrieveAPIView):
    permission_classes = [HasValidAppKey]
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer


class ConsultationAnswerCreateView(generics.CreateAPIView, generics.UpdateAPIView):
    permission_classes = [HasValidAppKey]
    serializer_class = ConsultationAnswerSerializer

    def create(self, request, *args, **kwargs):
        consultation_id = kwargs.get("pk")
        consultation = Consultation.objects.get(id=consultation_id)

        # Check if consultation already has an answer
        if hasattr(consultation, 'answer'):
            return Response(
                {"error": "Consultation already has an answer. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(consultant=request.flutter_user, consultation=consultation)

        consultation.status = "answered"
        consultation.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        consultation_id = kwargs.get("pk")
        consultation = Consultation.objects.get(id=consultation_id)
        
        # Check if consultation has an answer and if it's the same consultant
        if not hasattr(consultation, 'answer'):
            return Response(
                {"error": "No answer found. Use POST to create first answer."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if consultation.answer.consultant != request.flutter_user:
            return Response(
                {"error": "Only the original consultant can update the answer."},
                status=status.HTTP_403_FORBIDDEN
            )

        answer = consultation.answer
        serializer = self.get_serializer(answer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
