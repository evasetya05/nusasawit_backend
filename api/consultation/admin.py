from django.contrib import admin
from .models import Consultant, Consultation, ConsultationMessage


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
        'topic', 
        'status', 
        'consultant',
        'created_at'
    ]
    list_filter = ['status', 'consultant']
    search_fields = ['farmer__identifier', 'topic']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('farmer', 'topic')
        }),
        ('Assignment', {
            'fields': ('consultant', 'status')
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
        'sender_farmer',
        'sender_consultant',
        'created_at'
    ]
    list_filter = ['created_at', 'sender_consultant']
    search_fields = ['consultation__id', 'sender_farmer__identifier', 'content']
    readonly_fields = ['created_at',]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Message Info', {
            'fields': ('consultation', 'content', 'image')
        }),
        ('Sender Info', {
            'fields': ('sender_farmer', 'sender_consultant')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )