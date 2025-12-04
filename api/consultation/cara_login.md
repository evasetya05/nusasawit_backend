

Berikut pembaruan untuk fitur balasan konsultan:

1. **Backend View** (@api/consultation/views.py#1-184)  
   - Menambahkan [ConsultantDashboardView](cci:2://file:///home/eva/app/python/django/3.nusasawit_backend/nusasawit_backend/api/consultation/views.py:98:0-178:105) berbasis `TemplateView` yang hanya bisa diakses akun dengan relasi `consultant_profile`.  
   - Menampilkan daftar konsultasi milik konsultan, menampilkan pesan, dan menangani POST balasan (teks serta lampiran).  
   - Menjaga validasi (konsultasi wajib, isi/lampiran wajib, dll) serta memberi notifikasi via `messages`.

2. **Template Dashboard** (@api/consultation/templates/consultation/consultant_dashboard.html#1-118)  
   - UI dua kolom: daftar konsultasi di kiri dan percakapan + form balasan di kanan.  
   - Pesan otomatis scroll ke bawah, lampiran dapat diunduh, badge status jelas.

### Rekomendasi login konsultan
1. **Gunakan akun Django bawaan**: setiap konsultan punya `User` standar, login melalui `/admin/login/` atau view login khusus, lalu diarahkan ke dashboard baru ini.  
2. **Batasi akses**: pastikan hanya user dengan `user.consultant_profile` aktif yang bisa membuka dashboard; gunakan `LoginRequiredMixin` + pengecekan relasi (sudah diimplementasikan).  
3. **Opsional**: buat group/permission khusus (`is_consultant`) untuk mempermudah pengelolaan akses, terutama bila dashboard berada di luar admin panel.

Silakan jalankan `python manage.py runserver` lalu akses `/api/consultation/consultant-dashboard/` (pastikan URL dipetakan) dengan akun konsultan untuk mencoba balasan pesan.