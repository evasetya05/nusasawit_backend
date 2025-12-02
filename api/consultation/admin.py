from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from apps.core.models import Consultant
from .models import Consultation, ConsultationMessage





class ConsultationMessageInlineForm(forms.ModelForm):
    class Meta:
        model = ConsultationMessage
        fields = '__all__'

    def __init__(self, *args, parent_consultation=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Nonaktifkan pengeditan manual dari admin, diset otomatis oleh sistem
        for field_name in ('sender_farmer', 'sender_consultant'):
            if field_name in self.fields:
                self.fields[field_name].disabled = True

        # Permudah konsultan menulis balasan langsung dari inline
        if 'content' in self.fields:
            self.fields['content'].widget.attrs.setdefault(
                'placeholder', 'Tulis balasan konsultan di sini...'
            )
            self.fields['content'].widget.attrs.setdefault('rows', 2)

        if not self.instance.pk and parent_consultation:
            if parent_consultation.farmer_id and 'sender_farmer' in self.fields:
                self.fields['sender_farmer'].initial = parent_consultation.farmer
            if parent_consultation.consultant_id and 'sender_consultant' in self.fields:
                self.fields['sender_consultant'].initial = parent_consultation.consultant


class ConsultationMessageInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_consultation = self.instance

    def _construct_form(self, i, **kwargs):
        kwargs['parent_consultation'] = self.parent_consultation
        return super()._construct_form(i, **kwargs)


class ConsultationMessageInline(admin.TabularInline):
    """Menampilkan pesan sebagai inline di halaman Consultation."""
    model = ConsultationMessage
    form = ConsultationMessageInlineForm
    formset = ConsultationMessageInlineFormSet
    fields = (
        'sender_label',
        'sender_farmer',
        'sender_consultant',
        'content',
        'image',
        'created_at'
    )
    readonly_fields = (
        'sender_label',
        'sender_farmer',
        'sender_consultant',
        'created_at'
    )
    can_delete = False
    extra = 1 # Menampilkan satu form kosong untuk balasan baru
    ordering = ('created_at',)

    def has_change_permission(self, request, obj=None):
        return False

    def sender_label(self, obj):
        if not obj or not obj.pk:
            return "Balasan baru (konsultan)"
        if obj.sender_consultant_id:
            consultant_name = obj.sender_consultant.name or obj.sender_consultant.user or 'Konsultan'
            return f"Konsultan · {consultant_name}"
        if obj.sender_farmer_id:
            return f"Flutter User · {obj.sender_farmer.identifier}"
        return "Sistem"

    sender_label.short_description = "Pengirim"


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

    def save_formset(self, request, form, formset, change):
        """
        Saat menyimpan pesan baru dari inline, otomatis set pengirimnya
        adalah konsultan yang sedang login.
        """
        instances = formset.save(commit=False)
        parent_consultation = form.instance
        for instance in instances:
            if isinstance(instance, ConsultationMessage):
                if parent_consultation and not instance.consultation_id:
                    instance.consultation = parent_consultation
                if parent_consultation and not instance.sender_farmer_id and parent_consultation.farmer_id:
                    instance.sender_farmer = parent_consultation.farmer
                if not instance.sender_consultant_id:
                    if parent_consultation and parent_consultation.consultant_id:
                        instance.sender_consultant = parent_consultation.consultant
                    elif hasattr(request.user, 'consultant_profile'):
                        instance.sender_consultant = request.user.consultant_profile
            instance.save()
        super().save_formset(request, form, formset, change)


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