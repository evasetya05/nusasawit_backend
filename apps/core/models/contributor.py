from django.db import models
from django.conf import settings


class TipContributor(models.Model):
    name = models.CharField(max_length=50, unique=True, null=True, blank=True)
    consultant_name = models.CharField(max_length=255, blank=True, null=True, help_text="Nama konsultan/lembaga")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tip_contributor_profile',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.name