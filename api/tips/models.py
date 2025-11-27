from django.db import models

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
