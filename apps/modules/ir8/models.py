from django.db import models
from django.utils import timezone

# sesuai instruksi Anda:
from apps.core.models import Employee, Company

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='complaints')
    reporter = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    # contoh sederhana satu file; bisa diubah ke Attachment model untuk multiple files
    attachments = models.FileField(upload_to='complaint_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    reviewed_by = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviews')
    review_notes = models.TextField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=False, help_text='Jika dicentang, nama reporter disembunyikan pada tampilan publik')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        reporter_name = "Anonymous" if self.is_anonymous else getattr(self.reporter, 'name', None) or str(self.reporter)
        return f"[{self.get_status_display()}] {self.title} - {reporter_name}"
