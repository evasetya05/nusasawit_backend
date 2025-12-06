from datetime import date
from io import BytesIO
from PIL import Image

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from .person import Person


class Borongan(models.Model):
    """
    Model untuk pekerjaan borongan/piece rate employee
    """
    employee = models.ForeignKey(
        'Employee', on_delete=models.CASCADE, related_name='borongan'
    )
    pekerjaan = models.CharField(max_length=255)
    satuan = models.CharField(max_length=100)
    harga_borongan = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Borongan'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.pekerjaan} - {self.employee.name}"


class Employee(Person):
    PPH21_STATUS_CHOICES = [
        ('TK/0', 'TK/0 - Tidak Kawin, tanpa tanggungan'),
        ('TK/1', 'TK/1 - Tidak Kawin, 1 tanggungan'),
        ('TK/2', 'TK/2 - Tidak Kawin, 2 tanggungan'),
        ('TK/3', 'TK/3 - Tidak Kawin, 3 tanggungan'),
        ('K/0', 'K/0 - Kawin, tanpa tanggungan'),
        ('K/1', 'K/1 - Kawin, 1 tanggungan'),
        ('K/2', 'K/2 - Kawin, 2 tanggungan'),
        ('K/3', 'K/3 - Kawin, 3 tanggungan'),
        ('HB/0', 'HB/0 - Istri bekerja, tanpa tanggungan (penghasilan digabung dengan suami)'),
        ('HB/1', 'HB/1 - Istri bekerja, 1 tanggungan'),
        ('HB/2', 'HB/2 - Istri bekerja, 2 tanggungan'),
        ('HB/3', 'HB/3 - Istri bekerja, 3 tanggungan'),
    ]

    email = models.EmailField(unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='person')
    company = models.ForeignKey(
        'Company', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(
        'Department', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(
        'Position', on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    hire_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    resignation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='employee_photo', null=True, blank=True)
    kk = models.FileField(upload_to='document/kk', null=True, blank=True)
    ktp = models.FileField(upload_to='document/ktp', null=True, blank=True)
    npwp = models.FileField(upload_to='document/npwp', null=True, blank=True)
    emergency_contact = models.CharField(max_length=225, blank=True)
    
    # Area/Location
    desa = models.ForeignKey(
        'area.Desa', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Desa/Kelurahan',
        help_text='Desa/Kelurahan tempat tinggal karyawan'
    )

    # Compensation defaults
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    default_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], help_text='Tunjangan tetap bulanan')
    pph21_status = models.CharField(
        max_length=5,
        choices=PPH21_STATUS_CHOICES,
        blank=True,
        default='',
        verbose_name='Status Pajak PPh 21'
    )

    def save(self, *args, **kwargs):
        if self.photo:
            self.photo = self.compress_image(self.photo)
        super().save(*args, **kwargs)
    
    def compress_image(self, image_field):
        img = Image.open(image_field)
        img_format = img.format or 'JPEG'
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if img_format == 'PNG' and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
            img_format = 'JPEG'
        
        # Compress image to target 150KB
        quality = 85
        while True:
            output = BytesIO()
            if img_format == 'JPEG':
                img.save(output, format='JPEG', quality=quality, optimize=True)
            else:
                img.save(output, format=img_format, optimize=True)
            
            size = output.tell()
            if size <= 150 * 1024 or quality <= 10:  # 150KB target or minimum quality
                break
            quality -= 10
        
        output.seek(0)
        # Save with same name but compressed content
        from django.core.files.base import ContentFile
        import os
        name = os.path.basename(image_field.name)
        if img_format == 'JPEG':
            name = os.path.splitext(name)[0] + '.jpg'
        return ContentFile(output.getvalue(), name)

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        years = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        return years
