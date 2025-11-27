from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class KPICycle(models.Model):
    class Period(models.TextChoices):
        WEEKLY = 'weekly', 'Mingguan'
        MONTHLY = 'monthly', 'Bulanan'
        QUARTERLY = 'quarterly', 'Kuartalan'
        SEMIANNUAL = 'semiannual', 'Semesteran'
        ANNUAL = 'annual', 'Tahunan'

    company = models.ForeignKey('core.Company', on_delete=models.CASCADE, related_name='kpi_cycles')
    name = models.CharField(max_length=100)
    period = models.CharField(max_length=20, choices=Period.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.active and self.start_date <= today <= self.end_date

    def __str__(self):
        return f"{self.name} ({self.get_period_display()})"


class KPI(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    employee = models.ForeignKey('core.Employee', on_delete=models.CASCADE)
    supervisor = models.ForeignKey('core.Employee', null=True, blank=True, on_delete=models.SET_NULL, related_name='supervised_kpis')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50, blank=True)
    target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text=_("Weightage of the KPI in percentage (0-100)"),
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    cycle = models.ForeignKey(KPICycle, on_delete=models.PROTECT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_kpis')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.employee}"


class KPIPeriodTarget(models.Model):
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, related_name='period_targets')
    period_start = models.DateField()
    label = models.CharField(max_length=50)
    target_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = (('kpi', 'period_start'),)

    def __str__(self):
        return f"{self.kpi} - {self.label}"


class KPIEvaluation(models.Model):
    period_target = models.OneToOneField(KPIPeriodTarget, on_delete=models.CASCADE, related_name='evaluations')
    score = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, help_text=_("Notes by employee"))
    notes_supervisor = models.TextField(blank=True, help_text=_("Notes by supervisor"))
    evaluated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='kpi_evaluations')
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ['-evaluated_at']

    def __str__(self):

        return f"Eval {self.period_target.label} for {self.period_target.kpi}"
