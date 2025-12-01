from django.contrib import admin
from .models import Consultant, Consultation, ConsultationMessage, ConsultationAnswer, ConsultationImage


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'institution_name', 
        'created_at'
    ]
    search_fields = ['name', 'institution_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'institution_name', 'bio')
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


@admin.register(ConsultationImage)
class ConsultationImageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'consultation', 
        'uploaded_by',
        'consultant_uploader',
        'caption',
        'created_at'
    ]
    list_filter = ['created_at', 'uploaded_by', 'consultant_uploader']
    search_fields = ['consultation__id', 'caption']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Image Info', {
            'fields': ('consultation', 'image', 'caption')
        }),
        ('Uploader Info', {
            'fields': ('uploaded_by', 'consultant_uploader')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# Backward compatibility
admin.site.register(ConsultationAnswer)