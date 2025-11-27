from django.db import models
from apps.core.models import Employee

class OcaiQuestion(models.Model):
    category = models.CharField(max_length=50, null=True, blank=True)
    dimension = models.CharField(max_length=50, null=True, blank=True)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category}: {self.dimension}: {self.text}"


class OcaiAnswer(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE)
    question = models.ForeignKey(
        OcaiQuestion, on_delete=models.CASCADE, related_name='ocai_answer')
    current = models.IntegerField()
    expected = models.IntegerField()
    # submit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.question} - {self.current} : {self.expected}"
