from django.db import models

class APIKey(models.Model):

    class Meta:
        verbose_name_plural = "API Keys"
        ordering = ['-created_at']

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    label = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=128, unique=True)
