from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import SystemUser, Invitation

@admin.register(SystemUser)
class SystemUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'company', 'is_owner', 'is_employee', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Company', {'fields': ('company',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Company', {'fields': ('company',)}),
    )

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'company','created_by', 'status', 'created_at', 'expires_at')
    list_filter = ('status', 'company')
    search_fields = ('email', 'company__name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
