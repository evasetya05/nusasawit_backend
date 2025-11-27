from django.db import models
from django.utils.text import slugify
from django.conf import settings
from ckeditor.fields import RichTextField

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()  # Menggunakan CKEditor
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)  # Memungkinkan slug kosong
    penulis = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Menghasilkan slug otomatis jika slug belum diisi
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
