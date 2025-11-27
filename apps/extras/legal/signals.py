from django.dispatch import receiver
from django_registration.signals import user_registered
from .models import UserAgreement, Policy

@receiver(user_registered)
def create_user_agreement(sender, request, user, **kwargs):
    terms = Policy.objects.filter(
        type=Policy.DocType.TERMS_OF_SERVICE, is_active=True
    ).first()
    privacy = Policy.objects.filter(
        type=Policy.DocType.PRIVACY_POLICY, is_active=True
    ).first()
    UserAgreement.objects.create(user=user, policy=terms)
    UserAgreement.objects.create(user=user, policy=privacy)
