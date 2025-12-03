echo $DJANGO_SETTINGS_MODULE

export DJANGO_SETTINGS_MODULE=config.settings.production



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