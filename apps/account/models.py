from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


def default_expires_at():
    return timezone.now() + timezone.timedelta(days=7)


class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        EXPIRED = 'EXPIRED', 'Expired'
        REVOKED = 'REVOKED', 'Revoked'

    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(
        'core.Company', on_delete=models.CASCADE, related_name='invitations')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=default_expires_at)
    created_by = models.ForeignKey(
        'account.SystemUser', on_delete=models.CASCADE, related_name='sent_invitations')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Invitation for {self.email} ({self.status})"


class SystemUser(AbstractUser):
    invitation = models.OneToOneField(
        Invitation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user'
    )

    company = models.ForeignKey(
        'core.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    @property
    def invitation_status(self):
        if not self.invitation:
            return 'NOT_INVITED'
        return self.invitation.status

    def is_owner(self):
        company_owner = self.company.owner if self.company else None
        return company_owner == self
    is_owner.boolean = True

    def is_employee(self):
        return self.company and not self.is_owner()
    is_employee.boolean = True
