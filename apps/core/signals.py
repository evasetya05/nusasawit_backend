from django.dispatch import receiver
from django_registration.signals import user_activated
from .models import Company


@receiver(user_activated)
def user_activated_handler(sender, request, user, **kwargs):
    company_name = user.username + "'s Company"
    company = Company.objects.create(name=company_name, owner=user)
    user.company = company
    user.save(update_fields=['company'])
