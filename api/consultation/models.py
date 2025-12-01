from django.db import models
from django.utils import timezone
from api.user_flutter.models import FlutterUser


class Consultant(models.Model):
    """Model untuk data konsultan dengan keahlian dan pengalaman"""
    user = models.OneToOneField(
        FlutterUser,
        on_delete=models.CASCADE,
        related_name="consultant_profile"
    )
    
    name = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, help_text="Bio/deskripsi singkat konsultan")
    
    # Keahlian dan spesialisasi
    expertise_areas = models.JSONField(
        default=list,
        blank=True,
        help_text="List keahlian, misal: ['pertanian organik', 'hama tanaman', 'pupuk']"
    )
    specialization = models.CharField(
        max_length=100,
        blank=True,
        help_text="Spesialisasi utama"
    )
    
    # Pengalaman dan kualifikasi
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text="Pengalaman dalam tahun"
    )
    education = models.CharField(
        max_length=255,
        blank=True,
        help_text="Pendidikan terakhir"
    )
    certifications = models.JSONField(
        default=list,
        blank=True,
        help_text="List sertifikat/kualifikasi"
    )
    
    # Rating dan statistik
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        help_text="Rating rata-rata (0-5)"
    )
    total_consultations = models.PositiveIntegerField(
        default=0,
        help_text="Total konsultasi yang pernah ditangani"
    )
    
    # Status ketersediaan
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-rating", "-total_consultations", "name"]

    def __str__(self):
        return f"{self.name} - {self.specialization or 'General Consultant'}"


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
        related_name="consultation_messages"
    )
    
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default="question"
    )
    
    content = models.TextField(help_text="Isi pesan")
    
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
