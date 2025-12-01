from rest_framework import serializers
from .models import Consultant, Consultation, ConsultationMessage, ConsultationAnswer


class ConsultantSerializer(serializers.ModelSerializer):
    """Serializer untuk data konsultan dengan keahlian"""
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultant
        fields = [
            "id",
            "name",
            "institution_name",
            "bio",
            "expertise_areas",
            "specialization",
            "experience_years",
            "education",
            "certifications",
            "rating",
            "total_consultations",
            "is_active",
            "is_available",
            "user_info",
            "created_at",
        ]
    
    def get_user_info(self, obj):
        if obj.user:
            return {
                "identifier": obj.user.identifier,
                "email": obj.user.email,
                "phone_number": obj.user.phone_number,
            }
        return None


class ConsultationMessageSerializer(serializers.ModelSerializer):
    """Serializer untuk pesan dalam diskusi konsultasi"""
    sender_name = serializers.CharField(source="sender.identifier", read_only=True)
    consultant_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultationMessage
        fields = [
            "id", 
            "message_type", 
            "content", 
            "sender_name",
            "consultant_info",
            "created_at"
        ]
    
    def get_consultant_info(self, obj):
        if obj.consultant:
            return {
                "id": obj.consultant.id,
                "name": obj.consultant.name,
                "specialization": obj.consultant.specialization,
                "rating": obj.consultant.rating,
            }
        return None


class ConsultationSerializer(serializers.ModelSerializer):
    """Serializer untuk konsultasi dengan auto-assign consultant"""
    farmer_name = serializers.CharField(source="farmer.identifier", read_only=True)
    messages = ConsultationMessageSerializer(many=True, read_only=True)
    assigned_consultant_info = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    suggested_consultants = serializers.SerializerMethodField()

    def get_email(self, obj):
        request = self.context.get('request')
        if request:
            return request.headers.get('X-EMAIL')
        return None

    def get_phone(self, obj):
        request = self.context.get('request')
        if request:
            return request.headers.get('X-PHONE')
        return None
    
    def get_assigned_consultant_info(self, obj):
        if obj.assigned_consultant:
            return {
                "id": obj.assigned_consultant.id,
                "name": obj.assigned_consultant.name,
                "specialization": obj.assigned_consultant.specialization,
                "rating": obj.assigned_consultant.rating,
                "institution": obj.assigned_consultant.institution_name,
            }
        return None
    
    def get_suggested_consultants(self, obj):
        """Get suggested consultants based on category and expertise"""
        consultants = Consultant.objects.filter(
            is_active=True,
            is_available=True
        )
        
        if obj.category:
            # Filter by expertise areas matching category
            consultants = consultants.filter(
                expertise_areas__contains=[obj.category]
            )
        
        # Order by rating and experience
        consultants = consultants.order_by('-rating', '-experience_years')[:3]
        
        return ConsultantSerializer(consultants, many=True).data
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'flutter_user'):
            validated_data['farmer'] = request.flutter_user
        
        # Create consultation
        consultation = super().create(validated_data)
        
        # Auto-assign consultant if category provided
        if consultation.category:
            best_consultant = Consultant.objects.filter(
                is_active=True,
                is_available=True,
                expertise_areas__contains=[consultation.category]
            ).order_by('-rating', '-experience_years').first()
            
            if best_consultant:
                consultation.assigned_consultant = best_consultant
                consultation.status = "assigned"
                consultation.save()
        
        # Create initial message from the question
        ConsultationMessage.objects.create(
            consultation=consultation,
            sender=consultation.farmer,
            message_type="question",
            content=consultation.question
        )
        
        return consultation

    class Meta:
        model = Consultation
        fields = [
            "id",
            "farmer_name",
            "email",
            "phone",
            "question",
            "category",
            "status",
            "assigned_consultant_info",
            "suggested_consultants",
            "messages",
            "created_at",
            "updated_at",
        ]


# Backward compatibility
class ConsultationAnswerSerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(source="consultant.identifier", read_only=True)

    class Meta:
        model = ConsultationAnswer
        fields = ["id", "answer", "consultant_name", "institution_name", "answered_at"]
