from django.contrib import admin
from .models import KPICycle, KPI, KPIEvaluation, KPIPeriodTarget


@admin.register(KPICycle)
class KPICycleAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'period', 'start_date', 'end_date', 'active', 'is_active')
    list_filter = ('period', 'company', 'active')
    search_fields = ('name',)

    @admin.display(boolean=True, description='Is active based on date and active field')
    def is_active(self, obj):
        return obj.is_active


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('title', 'employee', 'supervisor', 'company', 'status', 'cycle', 'weight', 'target', 'created_at')
    list_filter = ('status', 'company', 'cycle')
    search_fields = ('title', 'employee__first_name', 'employee__last_name')


@admin.register(KPIEvaluation)
class KPIEvaluationAdmin(admin.ModelAdmin):
    list_display = ('period_target__kpi', 'period_target__label', 'score', 'evaluated_by', 'evaluated_at')
    list_filter = ('period_target__kpi__cycle__period',)
    search_fields = ('period_target__kpi__title', 'period_target__label')


@admin.register(KPIPeriodTarget)
class KPIPeriodTargetAdmin(admin.ModelAdmin):
    list_display = ('kpi', 'label', 'period_start', 'target_value')
    list_filter = ('kpi__cycle__period', 'kpi__status')
    search_fields = ('kpi__title', 'label')
