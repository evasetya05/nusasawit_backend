from django.db import models
from django.conf import settings


class Company(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='owned_company')
    address = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    PLAN_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Pro'),
    )
    plan = models.CharField(
        max_length=20, choices=PLAN_CHOICES, default='free')
    plan_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Companies'
