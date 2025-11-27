from django.contrib import admin
from .models import Company, Department, Position, Employee, Borongan


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
