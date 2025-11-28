from django.conf import settings
from django.db import models
from django.utils import timezone


class Consultation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("answered", "Answered"),
        ("closed", "Closed"),
    )

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultations"
    )
    
    question = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Konsultasi #{self.id} - {self.farmer}"


class ConsultationAnswer(models.Model):
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="answer"
    )
    
    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    answer = models.TextField()
    answered_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Jawaban untuk Konsultasi #{self.consultation.id}"
