# Area Models Implementation Summary

## Overview
Telah dibuat models untuk data wilayah Indonesia (Provinsi, Kabupaten/Kota, Kecamatan, Desa) dan diintegrasikan dengan Employee model.

## Models yang Dibuat

### 1. Provinsi
- **Fields:**
  - `kode`: CharField(2) - Kode provinsi (2 digit)
  - `nama`: CharField(100) - Nama provinsi

### 2. KabupatenKota
- **Fields:**
  - `provinsi`: ForeignKey ke Provinsi
  - `kode`: CharField(4) - Kode kabupaten/kota (4 digit)
  - `nama`: CharField(100) - Nama kabupaten/kota
  - `jenis`: CharField(10) - KABUPATEN atau KOTA

### 3. Kecamatan
- **Fields:**
  - `kabupaten_kota`: ForeignKey ke KabupatenKota
  - `kode`: CharField(6) - Kode kecamatan (6 digit)
  - `nama`: CharField(100) - Nama kecamatan

### 4. Desa
- **Fields:**
  - `kecamatan`: ForeignKey ke Kecamatan
  - `kode`: CharField(10) - Kode desa/kelurahan (10 digit)
  - `nama`: CharField(100) - Nama desa/kelurahan
  - `jenis`: CharField(10) - DESA atau KELURAHAN
  - `kode_pos`: CharField(5) - Kode pos (optional)
- **Property:**
  - `alamat_lengkap`: Mengembalikan alamat lengkap dari desa hingga provinsi

## Integrasi dengan Employee Model

### Employee Model
Ditambahkan field baru:
- `desa`: ForeignKey ke Desa (nullable, blank=True)

### Forms
- **EmployeeEditForm**: Ditambahkan field 'desa' untuk editing

## Template Updates

### employee_detail.html
Ditambahkan card "Area/Wilayah" yang menampilkan:
- Desa/Kelurahan
- Kecamatan
- Kabupaten/Kota
- Provinsi
- Kode Pos (jika ada)

### employee_edit.html
Ditambahkan card "Area/Wilayah" dengan:
- Form select untuk memilih Desa/Kelurahan
- Alert box yang menampilkan lokasi saat ini (jika sudah ada)

## Django Admin
Semua models telah diregistrasi di Django Admin dengan fitur:
- List display dengan kolom yang relevan
- Search fields untuk pencarian
- List filters untuk filtering
- Autocomplete fields untuk relasi

## Migrations
Migrations telah dibuat dan dijalankan:
- `area/0001_initial.py`: Membuat models Provinsi, KabupatenKota, Kecamatan, Desa
- `core/0002_employee_desa.py`: Menambahkan field desa ke Employee

## Langkah Selanjutnya

### 1. Import Data Wilayah Indonesia
Anda perlu mengisi database dengan data wilayah Indonesia. Anda bisa:
- Download data dari BPS (Badan Pusat Statistik)
- Gunakan data dari Kemendagri
- Import dari file CSV/JSON

Contoh script untuk import data:
```python
# management/commands/import_wilayah.py
from django.core.management.base import BaseCommand
from apps.modules.area.models import Provinsi, KabupatenKota, Kecamatan, Desa
import csv

class Command(BaseCommand):
    help = 'Import data wilayah Indonesia'

    def handle(self, *args, **options):
        # Import logic here
        pass
```

### 2. Tambahkan Widget Select2 (Optional)
Untuk memudahkan pencarian desa, Anda bisa menambahkan widget Select2:
```python
# forms.py
from django_select2.forms import ModelSelect2Widget

class EmployeeEditForm(forms.ModelForm):
    class Meta:
        widgets = {
            'desa': ModelSelect2Widget(
                model=Desa,
                search_fields=['nama__icontains', 'kode__icontains']
            )
        }
```

### 3. API Endpoint untuk Cascading Select (Optional)
Buat API endpoint untuk mendapatkan:
- Kabupaten/Kota berdasarkan Provinsi
- Kecamatan berdasarkan Kabupaten/Kota
- Desa berdasarkan Kecamatan

## Files Modified/Created

### Created:
1. `/apps/modules/area/models.py` - Area models
2. `/apps/modules/area/admin.py` - Admin registration
3. `/apps/modules/area/urls.py` - URL configuration
4. `/apps/modules/area/migrations/0001_initial.py` - Initial migration

### Modified:
1. `/apps/core/models/employee.py` - Added desa field
2. `/apps/modules/m3onboarding/forms.py` - Added desa to EmployeeEditForm
3. `/apps/modules/m3onboarding/templates/m3onboarding/struktur_organisasi/employee_detail.html` - Added Area card
4. `/apps/modules/m3onboarding/templates/m3onboarding/struktur_organisasi/employee_edit.html` - Added Area form card
5. `/apps/core/migrations/0002_employee_desa.py` - Migration for desa field

## Testing
Untuk menguji implementasi:
1. Akses Django Admin: `/admin/`
2. Tambahkan data Provinsi, Kabupaten/Kota, Kecamatan, dan Desa
3. Edit employee dan pilih Desa/Kelurahan
4. Lihat detail employee untuk melihat informasi wilayah
