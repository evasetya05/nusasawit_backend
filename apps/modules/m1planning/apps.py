from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class M1PlanningConfig(AppConfig):
    """Configuration for the M1 Planning module."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.modules.m1planning'
    verbose_name = _("Modul 1 Planning")
