"""Admin configuration for the M1 Planning module."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import LCRRecord


@admin.register(LCRRecord)
class LCRRecordAdmin(admin.ModelAdmin):
    """Admin configuration for LCR Records."""
    
    list_display = (
        'id',
        'company',
        'period',
        'formatted_income',
        'formatted_labor_cost',
        'formatted_lcr',
        'created_at',
    )
    
    list_filter = (
        'company',
        'period',
        'created_at',
    )
    
    search_fields = (
        'company__name',
        'period',
    )
    
    list_per_page = 20
    date_hierarchy = 'period'
    ordering = ('-period', '-created_at')
    
    fieldsets = (
        (_('Company Information'), {
            'fields': ('company', 'period')
        }),
        (_('Financial Information'), {
            'fields': ('total_income', 'total_labor_cost')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'formatted_lcr')
    
    def formatted_income(self, obj):
        return obj.formatted_income
    formatted_income.short_description = _("Income")
    formatted_income.admin_order_field = 'total_income'
    
    def formatted_labor_cost(self, obj):
        return obj.formatted_labor_cost
    formatted_labor_cost.short_description = _("Labor Cost")
    formatted_labor_cost.admin_order_field = 'total_labor_cost'
    
    def formatted_lcr(self, obj):
        return obj.formatted_lcr
    formatted_lcr.short_description = _("LCR %")
    
    def get_queryset(self, request):
        """Optimize database queries."""
        return super().get_queryset(request).select_related('company')
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete records."""
        return request.user.is_superuser
