from django.db import models
from django.utils import timezone
from api.user_flutter.models import FlutterUser
from django.conf import settings
from apps.core.models import Consultant





class Consultation(models.Model):
    farmer = models.ForeignKey(
        FlutterUser,
        on_delete=models.CASCADE,
        related_name="consultations"
    )
    consultant = models.ForeignKey(
        Consultant,
        on_delete=models.CASCADE,
        related_name="consultations",
        null=True,
        blank=True
    )
    
    topic = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ("open", "Open"),
            ("closed", "Closed"),
        ),
        default="open",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Konsultasi {self.id}"


class ConsultationMessage(models.Model):
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True
    )
    
    sender_farmer = models.ForeignKey(
        FlutterUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_messages"
    )
    sender_consultant = models.ForeignKey(
        Consultant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_consultant_messages"
    )

    content = models.TextField(null=True, blank=True)
    
    image = models.ImageField(
        upload_to="consultation_messages/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message {self.id}"
