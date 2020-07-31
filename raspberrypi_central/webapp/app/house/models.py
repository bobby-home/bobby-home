from django.db import models


class Location(models.Model):
    structure = models.CharField(max_length=60)
    sub_structure = models.CharField(max_length=60)

    def __str__(self):
        return '{0}_{1}'.format(self.structure, self.sub_structure)
    
    class Meta:
        unique_together = ['structure', 'sub_structure']
