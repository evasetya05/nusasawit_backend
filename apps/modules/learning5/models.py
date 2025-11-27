# apps/learning5/models.py
from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import Employee, Company

User = get_user_model()


class Competency(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or "(no name)"


class TrainingNeed(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assessments')
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name='main_competencies')
    detail_competency = models.ForeignKey(Competency, null=True, blank=True, on_delete=models.CASCADE, related_name='detail_competencies')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True, blank=True)
    current_score = models.PositiveSmallIntegerField(help_text='Score 0-5', null=True, blank=True)
    desired_score = models.PositiveSmallIntegerField(help_text='Score 0-5', null=True, blank=True)
    when_to_traine = models.DateField(null=True, blank=True)
    jenis_pelatihan = models.CharField(max_length=100, blank=True)
    done_at = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('employee', 'competency', 'detail_competency')

    def __str__(self):
        return f"{self.employee} - {self.competency} - {self.detail_competency}"
