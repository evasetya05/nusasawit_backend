from rest_framework import serializers
from .models import Consultant, Consultation, ConsultationMessage, ConsultationAnswer, ConsultationImage


class ConsultantSerializer(serializers.ModelSerializer):
    """Serializer untuk data konsultan yang sederhana"""
    
    class Meta:
        model = Consultant
        fields = [
            "id",
            "name",
            "institution_name",
            "bio",
            "created_at",
        ]


class ConsultationMessageSerializer(serializers.ModelSerializer):
    """Serializer untuk pesan dalam diskusi konsultasi"""
    sender_name = serializers.CharField(source="sender.identifier", read_only=True, allow_null=True)
    consultant_info = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultationMessage
        fields = [
            "id", 
            "message_type", 
            "content", 
            "sender_name",
            "consultant_info",
            "images",
            "created_at"
        ]
    
    def get_consultant_info(self, obj):
        if obj.consultant:
            return {
                "id": obj.consultant.id,
                "name": obj.consultant.name,
                "institution_name": obj.consultant.institution_name,
            }
        return None
    
    def get_images(self, obj):
        images = obj.images.all()
        return [
            {
                "id": img.id,
                "image_url": img.image.url if img.image else None,
                "caption": img.caption,
                "created_at": img.created_at,
            }
            for img in images
        ]


class ConsultationImageSerializer(serializers.ModelSerializer):
    """Serializer untuk gambar konsultasi"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultationImage
        fields = [
            "id",
            "image_url",
            "caption",
            "created_at",
        ]
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ConsultationSerializer(serializers.ModelSerializer):
    """Serializer untuk konsultasi"""
    farmer_name = serializers.CharField(source="farmer.identifier", read_only=True)
    messages = ConsultationMessageSerializer(many=True, read_only=True)
    assigned_consultant_info = serializers.SerializerMethodField()
    images = ConsultationImageSerializer(many=True, read_only=True, source="images.all")
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

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
                "institution_name": obj.assigned_consultant.institution_name,
                "bio": obj.assigned_consultant.bio,
            }
        return None
    
    def get_suggested_consultants(self, obj):
        """Get all available consultants"""
        consultants = Consultant.objects.all().order_by('name')[:10]
        return ConsultantSerializer(consultants, many=True).data
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'flutter_user'):
            validated_data['farmer'] = request.flutter_user
        
        # Create consultation
        consultation = super().create(validated_data)
        
        # Don't auto-assign consultant - let user choose from frontend
        
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
            "images",
            "created_at",
            "updated_at",
        ]


# Backward compatibility
class ConsultationAnswerSerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(source="consultant.identifier", read_only=True)

    class Meta:
        model = ConsultationAnswer
        fields = ["id", "answer", "consultant_name", "institution_name", "answered_at"]
