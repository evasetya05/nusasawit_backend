from django.contrib import admin
from .models import Consultant, Consultation, ConsultationMessage
from django.utils.html import format_html


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = [
        'display_profile_picture',
        'name',
        'institution_name', 
        'created_at'
    ]
    search_fields = ['name', 'institution_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'name', 'profile_picture', 'institution_name', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.profile_picture.url)
        return "No Image"
    display_profile_picture.short_description = 'Profile Picture'


class ConsultationMessageInline(admin.TabularInline):
    """Menampilkan pesan sebagai inline di halaman Consultation."""
    model = ConsultationMessage
    fields = ('sender_farmer', 'sender_consultant', 'content', 'created_at')
    readonly_fields = ('created_at', 'sender_farmer', 'sender_consultant')
    extra = 1 # Menampilkan satu form kosong untuk balasan baru
    ordering = ('created_at',)

    def has_change_permission(self, request, obj=None):
        return False


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
    inlines = [ConsultationMessageInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('farmer', 'topic',)
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

    def save_formset(self, request, form, formset, change):
        """
        Saat menyimpan pesan baru dari inline, otomatis set pengirimnya
        adalah konsultan yang sedang login.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ConsultationMessage) and hasattr(request.user, 'consultant_profile'):
                instance.sender_consultant = request.user.consultant_profile
                instance.save()
        formset.save_m2m()