from django.db import models
from django.utils import timezone
from api.user_flutter.models import FlutterUser


class Consultation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("answered", "Answered"),
        ("closed", "Closed"),
    )

    farmer = models.ForeignKey(
        FlutterUser,
        on_delete=models.CASCADE,
        related_name="consultations"
    )
    
    question = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"Konsultasi #{self.id} - {self.farmer}"


class ConsultationAnswer(models.Model):
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="answer"
    )
    
    consultant = models.ForeignKey(
        FlutterUser,
        on_delete=models.CASCADE,
        related_name="consultation_answers",
        null=True,
        blank=True
    )
    

    
    consultant_name = models.CharField(max_length=255, null=True, blank=True)
    institution_name = models.CharField(max_length=255, null=True, blank=True)

    answer = models.TextField(null=True, blank=True)

    answered_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"Jawaban untuk Konsultasi #{self.consultation.id} oleh {self.consultant_name}"
