from django.urls import path
from .views import (
    petunjuk_list, petunjuk_detail, kategori_list, 
    mark_as_read, user_read_history
)

app_name = 'petunjuk'

urlpatterns = [
    # Petunjuk endpoints
    path('', petunjuk_list, name='petunjuk_list'),
    path('<int:pk>/', petunjuk_detail, name='petunjuk_detail'),
    
    # Kategori endpoints
    path('kategori/', kategori_list, name='kategori_list'),
    
    # User interaction endpoints
    path('<int:petunjuk_id>/mark-read/', mark_as_read, name='mark_as_read'),
    path('read-history/', user_read_history, name='user_read_history'),
]

"""
CURL COMMANDS FOR PETUNJUK API ENDPOINTS

# Base URL: http://localhost:8000/api/petunjuk/
# Headers: -H "X-APP-KEY: your-app-key" -H "Content-Type: application/json"
# Auth: -H "Authorization: Token your-auth-token" (for protected endpoints)

# 1. GET all petunjuk
curl -X GET "http://localhost:8000/api/petunjuk/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json"

# 2. GET petunjuk by category
curl -X GET "http://localhost:8000/api/petunjuk/?kategori=1" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json"

# 3. GET specific petunjuk
curl -X GET "http://localhost:8000/api/petunjuk/1/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json"

# 4. POST create new petunjuk
curl -X POST "http://localhost:8000/api/petunjuk/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json" \
  -d '{
    "judul": "Cara Registrasi Akun",
    "kategori": 1,
    "konten": "Langkah-langkah untuk membuat akun baru...",
    "langkah_langkah": [
      "Buka aplikasi",
      "Klik tombol Daftar",
      "Isi formulir",
      "Verifikasi email"
    ],
    "gambar": "https://example.com/image.jpg",
    "urutan": 1,
    "aktif": true
  }'

# 5. PUT update petunjuk
curl -X PUT "http://localhost:8000/api/petunjuk/1/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json" \
  -d '{
    "judul": "Cara Registrasi Akun (Updated)",
    "konten": "Updated content...",
    "urutan": 2
  }'

# 6. DELETE petunjuk
curl -X DELETE "http://localhost:8000/api/petunjuk/1/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json"

# 7. GET all kategori
curl -X GET "http://localhost:8000/api/petunjuk/kategori/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json"

# 8. POST create new kategori
curl -X POST "http://localhost:8000/api/petunjuk/kategori/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Registrasi",
    "deskripsi": "Petunjuk untuk proses registrasi",
    "urutan": 1,
    "aktif": true
  }'

# 9. POST mark petunjuk as read (requires authentication)
curl -X POST "http://localhost:8000/api/petunjuk/1/mark-read/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token"

# 10. GET user read history (requires authentication)
curl -X GET "http://localhost:8000/api/petunjuk/read-history/" \
  -H "X-APP-KEY: your-app-key" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token"

# RESPONSE EXAMPLES:

# GET petunjuk response:
# {
#   "id": 1,
#   "judul": "Cara Registrasi Akun",
#   "kategori": 1,
#   "kategori_nama": "Registrasi",
#   "konten": "Langkah-langkah untuk membuat akun baru...",
#   "langkah_langkah": ["Buka aplikasi", "Klik tombol Daftar", "Isi formulir", "Verifikasi email"],
#   "gambar": "https://example.com/image.jpg",
#   "urutan": 1,
#   "aktif": true,
#   "created_at": "2025-11-29T12:00:00Z",
#   "updated_at": "2025-11-29T12:00:00Z",
#   "sudah_dibaca": false
# }

# GET kategori response:
# {
#   "id": 1,
#   "nama": "Registrasi",
#   "deskripsi": "Petunjuk untuk proses registrasi",
#   "urutan": 1,
#   "aktif": true
# }
"""