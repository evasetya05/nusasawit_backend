from django.contrib import admin
from .models import Policy, UserAgreement

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('type', 'version', 'is_active', 'created_at')
    list_filter = ('type', 'is_active')

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            Policy.objects.filter(type=obj.type).update(is_active=False)
        super().save_model(request, obj, form, change)

@admin.register(UserAgreement)
class UserAgreementAdmin(admin.ModelAdmin):
    list_display = ('user', 'policy', 'accepted_at', 'ip_address')
    list_filter = ('policy__type',)

