from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from ckeditor.fields import RichTextField

class Policy(models.Model):
    class DocType(models.TextChoices):
        PRIVACY_POLICY = "privacy", _("Privacy Policy")
        TERMS_OF_SERVICE = "terms", _("Terms of Service")
        LICENSE = "license", _("License")

    type = models.CharField(max_length=50, choices=DocType)
    version = models.CharField(max_length=20)
    content = RichTextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Policies"
        unique_together = ("type", "version")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} - v{self.version}"


class UserAgreement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "policy")
        ordering = ["-accepted_at"]

    def __str__(self):
        return f"{self.user} - {self.policy}"
