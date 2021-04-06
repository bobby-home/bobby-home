from django.db import models

class StepDone(models.Model):
    class Meta:
        get_latest_by = 'done_at'

    slug = models.CharField(max_length=100, unique=True)
    done_at = models.DateTimeField(auto_now_add=True)
