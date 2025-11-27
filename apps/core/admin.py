from django.contrib import admin
from .models import Company, Department, Position, Employee


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'plan', 'plan_expires_at', 'created_at')
    list_filter = ('owner', 'plan', 'plan_expires_at', 'created_at')
    search_fields = ('name', 'owner__username')
    ordering = ('-created_at',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name', 'department__name')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'department', 'position', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('name', )
