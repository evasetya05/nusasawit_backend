from django.db import models


class Provinsi(models.Model):
    """
    Model untuk data Provinsi di Indonesia
    """
    kode = models.CharField(max_length=2, unique=True, help_text="Kode provinsi (2 digit)")
    nama = models.CharField(max_length=100, help_text="Nama provinsi")
    
    class Meta:
        verbose_name = "Provinsi"
        verbose_name_plural = "Provinsi"
        ordering = ['nama']
    
    def __str__(self):
        return self.nama


class KabupatenKota(models.Model):
    """
    Model untuk data Kabupaten/Kota di Indonesia
    """
    JENIS_CHOICES = [
        ('KABUPATEN', 'Kabupaten'),
        ('KOTA', 'Kota'),
    ]
    
    provinsi = models.ForeignKey(
        Provinsi, 
        on_delete=models.CASCADE, 
        related_name='kabupaten_kota'
    )
    kode = models.CharField(max_length=4, unique=True, help_text="Kode kabupaten/kota (4 digit)")
    nama = models.CharField(max_length=100, help_text="Nama kabupaten/kota")
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES, default='KABUPATEN')
    
    class Meta:
        verbose_name = "Kabupaten/Kota"
        verbose_name_plural = "Kabupaten/Kota"
        ordering = ['nama']
    
    def __str__(self):
        return f"{self.get_jenis_display()} {self.nama}"


class Kecamatan(models.Model):
    """
    Model untuk data Kecamatan di Indonesia
    """
    kabupaten_kota = models.ForeignKey(
        KabupatenKota, 
        on_delete=models.CASCADE, 
        related_name='kecamatan'
    )
    kode = models.CharField(max_length=6, unique=True, help_text="Kode kecamatan (6 digit)")
    nama = models.CharField(max_length=100, help_text="Nama kecamatan")
    
    class Meta:
        verbose_name = "Kecamatan"
        verbose_name_plural = "Kecamatan"
        ordering = ['nama']
    
    def __str__(self):
        return f"Kec. {self.nama}"


class Desa(models.Model):
    """
    Model untuk data Desa/Kelurahan di Indonesia
    """
    JENIS_CHOICES = [
        ('DESA', 'Desa'),
        ('KELURAHAN', 'Kelurahan'),
    ]
    
    kecamatan = models.ForeignKey(
        Kecamatan, 
        on_delete=models.CASCADE, 
        related_name='desa'
    )
    kode = models.CharField(max_length=10, unique=True, help_text="Kode desa/kelurahan (10 digit)")
    nama = models.CharField(max_length=100, help_text="Nama desa/kelurahan")
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES, default='DESA')
    kode_pos = models.CharField(max_length=5, blank=True, null=True, help_text="Kode pos")
    
    class Meta:
        verbose_name = "Desa/Kelurahan"
        verbose_name_plural = "Desa/Kelurahan"
        ordering = ['nama']
    
    def __str__(self):
        return f"{self.get_jenis_display()} {self.nama}"
    
    @property
    def alamat_lengkap(self):
        """
        Mengembalikan alamat lengkap dari desa hingga provinsi
        """
        return f"{self.get_jenis_display()} {self.nama}, {self.kecamatan}, {self.kecamatan.kabupaten_kota}, {self.kecamatan.kabupaten_kota.provinsi}"
