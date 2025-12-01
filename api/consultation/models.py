from django.db import models
from django.utils import timezone
from api.user_flutter.models import FlutterUser


class Consultant(models.Model):
    """Model untuk data konsultan yang sederhana"""
    name = models.CharField(max_length=255)
    institution_name = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        help_text="Nama lembaga/institusi"
    )
    bio = models.TextField(
        null=True, 
        blank=True, 
        help_text="Bio/deskripsi singkat konsultan"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Consultation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("answered", "Answered"),
        ("closed", "Closed"),
    )

    farmer = models.ForeignKey(
        FlutterUser,
        on_delete=models.CASCADE,
        related_name="consultations"
    )
    
    question = models.TextField(null=True, blank=True, help_text="Pertanyaan dari petani")
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Kategori pertanyaan untuk matching konsultan"
    )
    
    # Auto-assign consultant
    assigned_consultant = models.ForeignKey(
        Consultant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_consultations"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Konsultasi #{self.id} - {self.farmer.identifier}"


class ConsultationMessage(models.Model):
    """Model untuk pesan dalam diskusi konsultasi (chat-style)"""
    MESSAGE_TYPES = (
        ("question", "Pertanyaan"),
        ("answer", "Jawaban"),
        ("follow_up", "Tindak Lanjut"),
        ("info", "Informasi"),
    )

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    
    sender = models.ForeignKey(
        FlutterUser,
        on_delete=models.CASCADE,
        related_name="consultation_messages",
        null=True,
        blank=True
    )
    
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default="question"
    )
    
    content = models.TextField(
        help_text="Isi pesan",
        null=True,
        blank=True
    )
    
    # Reference ke consultant jika jawaban dari konsultan
    consultant = models.ForeignKey(
        Consultant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultant_messages"
    )
    
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message #{self.id} in Consultation #{self.consultation.id}"


class ConsultationImage(models.Model):
    """Model untuk lampiran gambar dalam konsultasi"""
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="images"
    )
    
    message = models.ForeignKey(
        ConsultationMessage,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True
    )
    
    image = models.ImageField(
        upload_to='consultation_images/',
        help_text="Gambar untuk konsultasi"
    )
    
    uploaded_by = models.ForeignKey(
        FlutterUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_consultation_images"
    )
    
    consultant_uploader = models.ForeignKey(
        Consultant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_images"
    )
    
    caption = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Keterangan gambar"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Image for Consultation #{self.consultation.id}"


# Backward compatibility
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
