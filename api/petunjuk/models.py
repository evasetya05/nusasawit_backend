from django.db import models
from django.utils import timezone


class PetunjukKategori(models.Model):
    """
    Model untuk kategori petunjuk
    """
    nama = models.CharField(max_length=50, unique=True, help_text="Nama kategori")
    deskripsi = models.TextField(blank=True, null=True, help_text="Deskripsi kategori")
    urutan = models.PositiveIntegerField(default=0, help_text="Urutan tampilan")
    aktif = models.BooleanField(default=True, help_text="Status aktif/non-aktif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['urutan', 'nama']
        verbose_name = "Kategori Petunjuk"
        verbose_name_plural = "Kategori Petunjuk"
    
    def __str__(self):
        return self.nama


class Petunjuk(models.Model):
    """
    Model untuk menyimpan petunjuk penggunaan aplikasi
    yang akan dibaca oleh frontend Flutter
    """
    judul = models.CharField(max_length=200, help_text="Judul petunjuk")
    kategori = models.ForeignKey(
        PetunjukKategori,
        on_delete=models.CASCADE,
        related_name="petunjuk",
        help_text="Kategori petunjuk"
    )
    konten = models.TextField(help_text="Isi petunjuk dalam format teks")
    langkah_langkah = models.JSONField(default=list, blank=True, help_text="Array of steps untuk petunjuk berlangkah")
    gambar = models.URLField(null=True, blank=True, help_text="URL gambar pendukung")
    urutan = models.PositiveIntegerField(default=0, help_text="Urutan tampilan")
    aktif = models.BooleanField(default=True, help_text="Status aktif/non-aktif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['kategori', 'urutan', 'judul']
        verbose_name = "Petunjuk"
        verbose_name_plural = "Petunjuk"
    
    def __str__(self):
        return f"{self.judul} - {self.get_kategori_display()}"


class PetunjukBaca(models.Model):
    """
    Model untuk tracking petunjuk yang sudah dibaca oleh user
    """
    from django.conf import settings
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="petunjuk_dibaca"
    )
    petunjuk = models.ForeignKey(
        Petunjuk,
        on_delete=models.CASCADE,
        related_name="dibaca_oleh"
    )
    tanggal_baca = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'petunjuk']
        verbose_name = "Petunjuk Dibaca"
        verbose_name_plural = "Petunjuk Dibaca"
    
    def __str__(self):
        return f"{self.user} - {self.petunjuk.judul}"
