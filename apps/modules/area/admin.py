from django.contrib import admin
from .models import Provinsi, KabupatenKota, Kecamatan, Desa


@admin.register(Provinsi)
class ProvinsiAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama']
    search_fields = ['nama', 'kode']
    ordering = ['nama']


@admin.register(KabupatenKota)
class KabupatenKotaAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'jenis', 'provinsi']
    list_filter = ['jenis', 'provinsi']
    search_fields = ['nama', 'kode']
    ordering = ['nama']
    autocomplete_fields = ['provinsi']


@admin.register(Kecamatan)
class KecamatanAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'kabupaten_kota']
    list_filter = ['kabupaten_kota__provinsi']
    search_fields = ['nama', 'kode', 'kabupaten_kota__nama']
    ordering = ['nama']
    autocomplete_fields = ['kabupaten_kota']


@admin.register(Desa)
class DesaAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'jenis', 'kecamatan', 'kode_pos']
    list_filter = ['jenis', 'kecamatan__kabupaten_kota__provinsi']
    search_fields = ['nama', 'kode', 'kecamatan__nama', 'kode_pos']
    ordering = ['nama']
    autocomplete_fields = ['kecamatan']
