from django.db import models
from django.conf import settings


class DocumentStandar(models.Model):
    name = models.CharField(max_length=255, help_text="Nama dokumen")
    file = models.FileField(upload_to='sop_uploads/', help_text="File dokumen (maks 2 MB)")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_standar'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
