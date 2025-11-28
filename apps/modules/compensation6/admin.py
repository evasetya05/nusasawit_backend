from django.contrib import admin
from .models import Payroll, PayrollPeriod, Allowance, Deduction, WorkRequest
from api.user_flutter.models import FlutterUser

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'is_closed')

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'period', 'net_salary')

@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name', 'amount')

@admin.register(Deduction)
class DeductionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name', 'amount')


@admin.register(WorkRequest)
class WorkRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'title', 'start_date', 'end_date', 'due_date', 'flutter_user_info', 'created_at')
    list_filter = ('employee', 'start_date', 'created_at', 'flutter_user')
    search_fields = ('employee__name', 'title', 'description', 'flutter_user__email', 'flutter_user__phone_number')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def flutter_user_info(self, obj):
        if obj.flutter_user:
            info = []
            if obj.flutter_user.email:
                info.append(f"Email: {obj.flutter_user.email}")
            if obj.flutter_user.phone_number:
                info.append(f"Phone: {obj.flutter_user.phone_number}")
            return " | ".join(info) if info else "-"
        return "-"
    flutter_user_info.short_description = 'Flutter User'


@admin.register(FlutterUser)
class FlutterUserAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'email', 'phone_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('identifier', 'email', 'phone_number')
    readonly_fields = ('identifier', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
