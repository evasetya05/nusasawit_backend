
Perubahan utama:
- Menambahkan [TipContributorDashboardView](cci:2://file:///home/eva/app/python/django/3.nusasawit_backend/nusasawit_backend/api/tips/views.py:45:0-89:49) beserta [TipForm](cci:2://file:///home/eva/app/python/django/3.nusasawit_backend/nusasawit_backend/api/tips/views.py:33:0-42:9) di @api/tips/views.py#1-101 untuk memungkinkan kontributor terotentikasi membuat tip, melihat tip sendiri, dan menerima notifikasi keberhasilan/gagal.
- Menyediakan template dashboard berfokus penulisan tip di @api/tips/templates/consultation/tip_contributor_dashboard.html#1-112 dengan form, validasi, dan daftar tip milik kontributor.
- Menambahkan rute web `/api/tips/contributor-dashboard/` di @api/tips/urls.py#1-11 agar dashboard dapat diakses setelah login.

Login terbaik untuk kontributor:
1. Gunakan akun Django standar; hubungkan user ke model [TipContributor](cci:2://file:///home/eva/app/python/django/3.nusasawit_backend/nusasawit_backend/api/tips/models.py:4:0-16:24) (mis. via field `user` sehingga `user.tip_contributor_profile` tersedia).
2. Batasi akses dashboard menggunakan `LoginRequiredMixin` dan cek relasi profiling (sudah diterapkan), sehingga hanya user yang terdaftar sebagai kontributor yang dapat menulis tip.
3. Opsional: buat grup/permission `is_tip_contributor` agar kontrol akses makin mudah bila jumlah peran bertambah.