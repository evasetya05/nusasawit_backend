from django.db import models
from django.conf import settings
from .person import Person


class Employee(Person):
    email = models.EmailField(unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='person')
    department = models.ForeignKey(
        'Department', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(
        'Position', on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    hire_date = models.DateField(null=True, blank=True)
    resignation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='employee_photo', null=True, blank=True)
    kk = models.FileField(upload_to='document/kk', null=True, blank=True)
    ktp = models.FileField(upload_to='document/ktp', null=True, blank=True)
    npwp = models.FileField(upload_to='document/npwp', null=True, blank=True)
