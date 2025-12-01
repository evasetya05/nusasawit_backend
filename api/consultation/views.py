from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permission import HasValidAppKey

from .models import Consultation, ConsultationMessage, Consultant, ConsultationAnswer
from .serializers import (
    ConsultationSerializer, 
    ConsultationMessageSerializer,
    ConsultantSerializer,
    ConsultationAnswerSerializer
)


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


class ConsultationMessageListCreateView(generics.ListCreateAPIView):
    """View untuk menambahkan pesan dalam konsultasi (chat-style)"""
    permission_classes = [HasValidAppKey]
    serializer_class = ConsultationMessageSerializer
    
    def get_queryset(self):
        consultation_id = self.kwargs['pk']
        return ConsultationMessage.objects.filter(consultation_id=consultation_id)
    
    def perform_create(self, serializer):
        consultation_id = self.kwargs['pk']
        consultation = Consultation.objects.get(id=consultation_id)
        
        # Auto-assign consultant if not assigned and this is an answer
        if not consultation.assigned_consultant and hasattr(self.request, 'flutter_user'):
            try:
                consultant = Consultant.objects.get(user=self.request.flutter_user)
                consultation.assigned_consultant = consultant
                consultation.status = "answered"
                consultation.save()
                
                # Set consultant in message
                serializer.save(
                    consultation=consultation,
                    sender=self.request.flutter_user,
                    consultant=consultant,
                    message_type="answer"
                )
                return
            except Consultant.DoesNotExist:
                pass
        
        # Regular message creation
        message_type = self.request.data.get('message_type', 'follow_up')
        serializer.save(
            consultation=consultation,
            sender=self.request.flutter_user,
            message_type=message_type
        )


class ConsultantListView(generics.ListAPIView):
    """View untuk melihat daftar konsultan yang tersedia"""
    permission_classes = [HasValidAppKey]
    serializer_class = ConsultantSerializer
    
    def get_queryset(self):
        queryset = Consultant.objects.filter(is_active=True, is_available=True)
        
        # Filter by specialization if provided
        specialization = self.request.query_params.get('specialization')
        if specialization:
            queryset = queryset.filter(
                expertise_areas__contains=[specialization]
            )
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(
                expertise_areas__contains=[category]
            )
        
        return queryset.order_by('-rating', '-experience_years')


class ConsultantAssignView(generics.UpdateAPIView):
    """View untuk meng-assign konsultan secara manual ke konsultasi"""
    permission_classes = [HasValidAppKey]
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    
    def update(self, request, *args, **kwargs):
        consultation = self.get_object()
        consultant_id = request.data.get('consultant_id')
        
        if not consultant_id:
            return Response(
                {"error": "consultant_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            consultant = Consultant.objects.get(id=consultant_id, is_active=True, is_available=True)
            consultation.assigned_consultant = consultant
            consultation.status = "assigned"
            consultation.save()
            
            return Response({
                "message": f"Consultant {consultant.name} assigned successfully",
                "consultant_info": ConsultantSerializer(consultant).data
            })
        except Consultant.DoesNotExist:
            return Response(
                {"error": "Consultant not found or not available"}, 
                status=status.HTTP_404_NOT_FOUND
            )


# Backward compatibility
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
