from django.db import models
from django.utils import timezone
from apps.core.models import Employee

class OcaiQuestion(models.Model):
    category = models.CharField(max_length=50, null=True, blank=True)
    dimension = models.CharField(max_length=50, null=True, blank=True)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category}: {self.dimension}: {self.text}"


def current_year():
    return timezone.now().year

def current_half():
    return 1 if timezone.now().month <= 6 else 2

class OcaiAnswer(models.Model):
    HALF_CHOICES = (
        (1, 'H1'),  # Jan–Jun
        (2, 'H2'),  # Jul–Dec
    )

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE)
    question = models.ForeignKey(
        OcaiQuestion, on_delete=models.CASCADE, related_name='ocai_answer')
    current = models.IntegerField()
    expected = models.IntegerField()
    submit_date = models.DateTimeField(null=True, blank=True)

    # Periodization fields (every 6 months)
    period_year = models.IntegerField(default=current_year)
    period_half = models.IntegerField(choices=HALF_CHOICES, default=current_half)

    class Meta:
        unique_together = ('employee', 'question', 'period_year', 'period_half')

    def __str__(self):
        label = 'H1' if self.period_half == 1 else 'H2'
        return f"{self.employee} - {self.question} - {self.current}:{self.expected} [{self.period_year}-{label}]"
