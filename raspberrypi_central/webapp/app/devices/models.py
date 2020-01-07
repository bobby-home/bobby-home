from django.db import models

class Locations(models.Model):
    structure = models.CharField(max_length=60)
    sub_structure = models.CharField(max_length=60)
