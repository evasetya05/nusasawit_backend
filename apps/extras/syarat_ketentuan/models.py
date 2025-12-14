from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class SyaratKetentuan(models.Model):
    title = models.CharField(max_length=200, default="Syarat dan Ketentuan")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Syarat dan Ketentuan"
        verbose_name_plural = "Syarat dan Ketentuan"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('syarat_ketentuan:syarat_dan_ketentuan_detail')


class KebijakanPrivasi(models.Model):
    title = models.CharField(max_length=200, default="Kebijakan Privasi")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kebijakan Privasi"
        verbose_name_plural = "Kebijakan Privasi"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('syarat_ketentuan:kebijakan_privasi_detail')