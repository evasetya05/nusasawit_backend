from django.db import models


class CertificationScheme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class CertificationSchemeDetail(models.Model):
    scheme = models.ForeignKey(
        CertificationScheme,
        on_delete=models.CASCADE,
        related_name="details"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.scheme.name} - {self.title}"
