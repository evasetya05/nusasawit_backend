from django.contrib import admin
from .models import OcaiQuestion, OcaiAnswer

admin.site.register(OcaiQuestion)
admin.site.register(OcaiAnswer)
