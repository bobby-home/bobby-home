from django.db import models
from .helpers import generate_key

class APIKey(models.Model):

    class Meta:
        verbose_name_plural = "API Keys"
        ordering = ['-created_at']

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    label = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_key()
            # messages.add_message(request, messages.WARNING, ('The API Key for %s is %s. Please note it since you will not be able to see it again.' % (self.label, obj.key)))
        super(APIKey, self).save(*args, **kwargs)
