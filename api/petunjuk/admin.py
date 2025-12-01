from django.contrib import admin
from .models import PetunjukKategori, Petunjuk, PetunjukBaca


# -------------------------------
# Inline untuk menampilkan Petunjuk di halaman kategori
# -------------------------------
class PetunjukInline(admin.TabularInline):
    model = Petunjuk
    extra = 1
    fields = ['judul', 'urutan', 'aktif']
    ordering = ['urutan']


# -------------------------------
# Admin untuk PetunjukKategori
# -------------------------------
@admin.register(PetunjukKategori)
class PetunjukKategoriAdmin(admin.ModelAdmin):
    list_display = ['nama', 'urutan', 'aktif', 'created_at']
    list_filter = ['aktif']
    search_fields = ['nama', 'deskripsi']
    ordering = ['urutan', 'nama']

    inlines = [PetunjukInline]

    readonly_fields = ['created_at', 'updated_at']


# -------------------------------
# Admin untuk Petunjuk
# -------------------------------
@admin.register(Petunjuk)
class PetunjukAdmin(admin.ModelAdmin):
    list_display = [
        'judul',
        'kategori',
        'urutan',
        'aktif',
        'updated_at'
    ]

    list_filter = ['kategori', 'aktif']
    search_fields = ['judul', 'konten']
    ordering = ['kategori', 'urutan', 'judul']

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informasi Utama', {
            'fields': (
                'judul',
                'kategori',
                'konten',
                'langkah_langkah',
                'gambar',
            )
        }),
        ('Pengaturan', {
            'fields': (
                'urutan',
                'aktif',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )


# -------------------------------
# Admin untuk PetunjukBaca
# -------------------------------
@admin.register(PetunjukBaca)
class PetunjukBacaAdmin(admin.ModelAdmin):
    list_display = ['user', 'petunjuk', 'tanggal_baca']
    list_filter = ['tanggal_baca', 'user']
    search_fields = ['user__username', 'petunjuk__judul']
    ordering = ['-tanggal_baca']

    readonly_fields = ['tanggal_baca']
