from django.db import models
from django.conf import settings
from apps.core.models import TipContributor
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os




class Tip(models.Model):
    CATEGORY_CHOICES = [
        ('Pembibitan', 'Pembibitan'),
        ('Penanaman', 'Penanaman'),
        ('Pemupukan', 'Pemupukan'),
        ('Perawatan', 'Perawatan'),
        ('Panen', 'Panen'),
        ('Pengolahan', 'Pengolahan'),
        ('Manajemen', 'Manajemen'),
        ('Pemasaran', 'Pemasaran'),
        ('Teknologi', 'Teknologi'),
        ('Lainnya', 'Lainnya'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='tips/', blank=True, null=True)
    contributor = models.ForeignKey(TipContributor, on_delete=models.CASCADE, related_name="tips", null=True, blank=True)
    discussion = models.TextField(blank=True, null=True, help_text="Identifier dari user flutter untuk diskusi")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate 16:9 aspect ratio
            width, height = img.size
            target_ratio = 16 / 9
            
            # Calculate new dimensions maintaining 16:9 ratio
            if width / height > target_ratio:
                new_height = height
                new_width = int(height * target_ratio)
            else:
                new_width = width
                new_height = int(width / target_ratio)
            
            # Crop to center
            left = (width - new_width) // 2
            top = (height - new_height) // 2
            right = left + new_width
            bottom = top + new_height
            img = img.crop((left, top, right, bottom))
            
            # Resize to mobile-friendly size (e.g., 800x450)
            img = img.resize((800, 450), Image.Resampling.LANCZOS)
            
            # Compress to under 100KB
            output = BytesIO()
            quality = 95
            while quality > 10:
                output.seek(0)
                output.truncate()
                img.save(output, format='JPEG', quality=quality)
                if output.tell() <= 100 * 1024:  # 100KB
                    break
                quality -= 5
            
            # Save the processed image
            self.image.save(os.path.basename(self.image.name), ContentFile(output.read()), save=False)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TipDiscussion(models.Model):
    tip = models.ForeignKey(Tip, on_delete=models.CASCADE, related_name="discussions")
    user_identifier = models.TextField(help_text="Identifier dari user flutter")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Diskusi untuk {self.tip.title} oleh {self.user_identifier}"
