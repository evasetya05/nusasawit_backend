from django.contrib import admin
from .models import Consultant, Consultation, ConsultationMessage, ConsultationAnswer


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'institution_name', 
        'specialization', 
        'experience_years', 
        'rating', 
        'total_consultations',
        'is_active',
        'is_available'
    ]
    list_filter = ['is_active', 'is_available', 'specialization']
    search_fields = ['name', 'institution_name', 'specialization']
    readonly_fields = ['rating', 'total_consultations', 'created_at', 'updated_at']
    ordering = ['-rating', '-total_consultations', 'name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'name', 'institution_name', 'bio')
        }),
        ('Expertise', {
            'fields': ('specialization', 'expertise_areas')
        }),
        ('Experience', {
            'fields': ('experience_years', 'education', 'certifications')
        }),
        ('Statistics', {
            'fields': ('rating', 'total_consultations'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'farmer', 
        'category', 
        'status', 
        'assigned_consultant',
        'created_at'
    ]
    list_filter = ['status', 'category', 'assigned_consultant']
    search_fields = ['farmer__identifier', 'question', 'category']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('farmer', 'category', 'question')
        }),
        ('Assignment', {
            'fields': ('assigned_consultant', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConsultationMessage)
class ConsultationMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'consultation', 
        'sender', 
        'message_type', 
        'consultant',
        'created_at'
    ]
    list_filter = ['message_type', 'consultant', 'created_at']
    search_fields = ['consultation__id', 'sender__identifier', 'content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Message Info', {
            'fields': ('consultation', 'sender', 'message_type', 'content')
        }),
        ('Consultant Info', {
            'fields': ('consultant',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# Backward compatibility
admin.site.register(ConsultationAnswer)