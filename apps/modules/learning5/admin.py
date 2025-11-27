# apps/learning5/admin.py
from django.contrib import admin
from .models import Competency, TrainingNeed


@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    list_display = ('name',  'description')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(TrainingNeed)
class TrainingNeedAdmin(admin.ModelAdmin):
    list_display = ('employee', 'competency', 'detail_competency', 'current_score', 'desired_score', 'when_to_traine')
    list_filter = ('competency',)
    search_fields = ('employee__user__username', 'competency__name')
