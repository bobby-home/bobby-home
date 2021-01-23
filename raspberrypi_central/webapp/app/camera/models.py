from django.db import models

from devices.models import Device


class CameraROI(models.Model):
    device = models.OneToOneField(Device, on_delete=models.PROTECT)

    """
    We save the picture where the user defined the ROI.
    This could be useful to check if the camera moves to let know the user
    because the ROI could become wrong.
    """
    define_picture = models.ImageField()


class CameraRectangleROIManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(disabled=False)


class CameraRectangleROI(models.Model):
    class Meta:
        default_manager_name = 'objects'

    objects = models.Manager()
    actives = CameraRectangleROIManager()

    # ? We might rework the max_digits & decimal_places here
    # I didn't really know what to put here. Seems good but may not be optimized.

    x = models.DecimalField(max_digits=8, decimal_places=4)
    y = models.DecimalField(max_digits=8, decimal_places=4)
    w = models.DecimalField(max_digits=8, decimal_places=4)
    h = models.DecimalField(max_digits=8, decimal_places=4)

    disabled = models.BooleanField(default=False)

    camera_roi = models.ForeignKey(CameraROI, on_delete=models.CASCADE)


class CameraMotionDetected(models.Model):
    event_ref = models.UUIDField(unique=True)

    motion_started_at = models.DateTimeField()
    motion_ended_at = models.DateTimeField(blank=True, null=True)

    motion_started_picture = models.ImageField()
    motion_ended_picture = models.ImageField(blank=True, null=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT)
    in_rectangle_roi = models.ManyToManyField(CameraRectangleROI, blank=True)

class CameraMotionDetectedBoundingBox(models.Model):
    """
    This is given by Tensorflow, they are bounding boxes around an object.
    This coordinates have been rescaled on the picture, they are not relatives ([0;1]).
    """
    x = models.DecimalField(max_digits=8, decimal_places=4)
    y = models.DecimalField(max_digits=8, decimal_places=4)
    w = models.DecimalField(max_digits=8, decimal_places=4)
    h = models.DecimalField(max_digits=8, decimal_places=4)

    camera_motion_detected = models.ForeignKey(CameraMotionDetected, on_delete=models.CASCADE)


class CameraMotionDetectedPicture(models.Model):
    event_ref = models.UUIDField()

    created_at = models.DateTimeField(auto_now_add=True)

    motion_started_picture = models.ImageField()
    motion_ended_picture = models.ImageField(blank=True, null=True)

    device = models.ForeignKey(Device, on_delete=models.PROTECT)
