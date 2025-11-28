from django.conf import settings
from django.db import models
from django.utils import timezone


class CertificationScheme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class CertificationProgress(models.Model):
    STATUS_CHOICES = (
        ("not_started", "Belum Mulai"),
        ("in_progress", "Dalam Proses"),
        ("completed", "Selesai"),
        ("revoked", "Dicabut"),
    )

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certifications"
    )
    scheme = models.ForeignKey(
        CertificationScheme,
        on_delete=models.CASCADE,
        related_name="progresses"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")
    start_date = models.DateField(default=timezone.localdate)
    completion_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.farmer} - {self.scheme}"


class CertificationTask(models.Model):
    PROGRESS_STATUS = (
        ("pending", "Menunggu"),
        ("in_progress", "Dalam Proses"),
        ("done", "Selesai"),
    )

    certification = models.ForeignKey(
        CertificationProgress,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    planned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PROGRESS_STATUS, default="pending")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tugas {self.title}"
