from datetime import date

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from .person import Person


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

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        years = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        return years
