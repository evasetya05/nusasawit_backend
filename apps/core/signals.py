from django.dispatch import receiver
from django_registration.signals import user_activated
from django.contrib.auth.models import Group
from django.db import transaction

from .models import Company

@receiver(user_activated)
def user_activated_handler(sender, request, user, **kwargs):
    with transaction.atomic():
        if getattr(user, 'company_id', None):
            company = user.company
        else:
            company_name = user.username + "'s Company"
            company = Company.objects.create(name=company_name, owner=user)
            user.company = company
            user.save(update_fields=['company'])

    group = Group.objects.get(name='Owner')
    user.groups.add(group)
