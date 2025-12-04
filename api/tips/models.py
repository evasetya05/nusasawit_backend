from django.db import models
from django.conf import settings
from apps.core.models import TipContributor




class Tip(models.Model):
    CATEGORY_CHOICES = [
        ('Pembibitan', 'Pembibitan'),
        ('Penanaman', 'Penanaman'),
        ('Pemupukan', 'Pemupukan'),
        ('Perawatan', 'Perawatan'),
        ('Panen', 'Panen'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image_url = models.URLField(blank=True, null=True)
    contributor = models.ForeignKey(TipContributor, on_delete=models.CASCADE, related_name="tips", null=True, blank=True)
    discussion = models.TextField(blank=True, null=True, help_text="Identifier dari user flutter untuk diskusi")
    created_at = models.DateTimeField(auto_now_add=True)

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
