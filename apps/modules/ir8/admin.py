from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'status', 'created_at', 'reviewed_by')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'reporter____username', 'reporter__email')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
