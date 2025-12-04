from django.contrib import admin
from django.utils.html import format_html
from .models import Company, Department, Position, Employee, Borongan, Consultant

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


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'plan', 'plan_expires_at', 'created_at')
    list_filter = ('owner', 'plan', 'plan_expires_at', 'created_at')
    search_fields = ('name', 'owner__username')
    ordering = ('-created_at',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department', 'department__company')
    search_fields = ('name', 'department__name')


class BoronganInline(admin.TabularInline):
    model = Borongan
    extra = 1
    fields = ('pekerjaan', 'satuan', 'harga_borongan')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'company',
                    'department', 'position', 'is_active')
    list_filter = ('department', 'company', 'is_active')
    search_fields = ('name', )
    inlines = [BoronganInline]


@admin.register(Borongan)
class BoronganAdmin(admin.ModelAdmin):
    list_display = ('pekerjaan', 'employee', 'satuan', 'harga_borongan', 'created_at')
    list_filter = ('employee__company', 'created_at')
    search_fields = ('pekerjaan', 'employee__name')
    ordering = ('-created_at',)


from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ConsultantAdminForm(forms.ModelForm):
    username = forms.CharField(required=False, help_text="Required if creating a new user")
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Required if creating a new user")

    class Meta:
        model = Consultant
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not user and (not username or not password):
            # If no user selected, must provide username and password to create one
            if not self.instance.pk: # Only enforce on creation
                raise forms.ValidationError("Please select an existing user OR provide username and password to create a new one.")
        
        if username and User.objects.filter(username=username).exists():
             raise forms.ValidationError(f"User with username '{username}' already exists.")

        return cleaned_data

    def save(self, commit=True):
        consultant = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not consultant.user and username and password:
            user = User.objects.create_user(username=username, password=password)
            consultant.user = user
        
        if commit:
            consultant.save()
        return consultant

# Re-register Consultant with the new form
admin.site.unregister(Consultant)
@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    form = ConsultantAdminForm
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
        ('User Account', {
            'fields': ('user', 'username', 'password'),
            'description': 'Select an existing user OR enter username/password to create a new one.'
        }),
        ('Basic Info', {
            'fields': ('name', 'profile_picture', 'institution_name', 'bio')
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


from .models import TipContributor

class TipContributorAdminForm(forms.ModelForm):
    username = forms.CharField(required=False, help_text="Required if creating a new user")
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Required if creating a new user")

    class Meta:
        model = TipContributor
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not user and (not username or not password):
            # If no user selected, must provide username and password to create one
            if not self.instance.pk: # Only enforce on creation
                raise forms.ValidationError("Please select an existing user OR provide username and password to create a new one.")
        
        if username and User.objects.filter(username=username).exists():
             raise forms.ValidationError(f"User with username '{username}' already exists.")

        return cleaned_data

    def save(self, commit=True):
        contributor = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not contributor.user and username and password:
            user = User.objects.create_user(username=username, password=password)
            contributor.user = user
        
        if commit:
            contributor.save()
        return contributor

@admin.register(TipContributor)
class TipContributorAdmin(admin.ModelAdmin):
    form = TipContributorAdminForm
    list_display = ['name', 'consultant_name', 'user']
    search_fields = ['name', 'consultant_name']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'username', 'password'),
            'description': 'Select an existing user OR enter username/password to create a new one.'
        }),
        ('Basic Info', {
            'fields': ('name', 'consultant_name')
        }),
    )
