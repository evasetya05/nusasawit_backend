from datetime import date
from io import BytesIO
from PIL import Image

from django.db import models
from django.conf import settings

class Consultant(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultant_profile')
    profile_picture = models.ImageField(upload_to='consultant_profiles/', null=True, blank=True)
    institution_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.profile_picture:
            self.profile_picture = self.compress_image(self.profile_picture)
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

    def __str__(self):
        return self.name or "Consultant"
