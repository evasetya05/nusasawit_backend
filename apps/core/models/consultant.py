from django.db import models
from django.conf import settings

class Consultant(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultant_profile')
    profile_picture = models.ImageField(upload_to='consultant_profiles/', null=True, blank=True)
    institution_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name or "Consultant"
