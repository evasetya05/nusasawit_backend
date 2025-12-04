echo $DJANGO_SETTINGS_MODULE

export DJANGO_SETTINGS_MODULE=config.settings.production

Hubungan antara pengguna dan perusahaan diperiksa melalui rantai: user -> person -> company.

Secara visual, alurnya seperti ini: request.user (Objek SystemUser) → .person (Objek Person/Employee) → .company (Objek Company)

update COMPANY KE USER HARUS 2 KALI 
PERTAMA DI EMPLOYEE MODEL
DAN DY SYSTEM USER

=== ATTENDANCE FORM DEBUG ===
User: pengecek1
Person: pengecek1
Is Owner: <bound method SystemUser.is_owner of <SystemUser: pengecek1>>
Branch: OWNER
Final employee queryset: [(2, 'mitra_borongan_1'), (4, 'mitra_borongan_2'), (1, 'pengecek1'), (3, 'pengecek 2')]
===========================


Logic untuk menentukan supervisor ada di beberapa file:

**1. [apps/core/templatetags/sidebar_menu.py](cci:7://file:///home/eva/app/python/django/3.nusasawit_backend/nusasawit_backend/apps/core/templatetags/sidebar_menu.py:0:0-0:0) (line 80):**
```python
is_supervisor = bool(person and person.subordinates.exists())
```

**2. [apps/core/views/index_views.py](cci:7://file:///home/eva/app/python/django/3.nusasawit_backend/nusasawit_backend/apps/core/views/index_views.py:0:0-0:0) (line 23):**
```python
is_supervisor = bool(person and person.subordinates.exists())
```

**3. `apps/core/models/employee.py` (line 58):**
Model Employee punya field `manager` dengan `related_name='subordinates'`

**Logicnya:**
- Supervisor = Employee yang punya subordinates (bawahan)
- Dicek dengan `person.subordinates.exists()` 
- `person` adalah Employee object yang terhubung ke user via `user.person`

**Masalah sekarang:** Debug menunjukkan `person exists: False` untuk kedua user, berarti `user.person` tidak ada. User `mitra1` dan `pengecek1` tidak terhubung ke Employee record, jadi tidak bisa dicek sebagai supervisor/employee.