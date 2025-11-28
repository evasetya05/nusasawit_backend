from django.contrib import admin
from .models import CertificationScheme, CertificationProgress, CertificationTask

admin.site.register(CertificationScheme)
admin.site.register(CertificationProgress)
admin.site.register(CertificationTask)