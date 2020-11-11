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


class CameraRectangleROI(models.Model):
    # ? We might rework the max_digits & decimal_places here
    # I didn't really know what to put here. Seems good but may not be optimized.

    x = models.DecimalField(max_digits=8, decimal_places=4)
    y = models.DecimalField(max_digits=8, decimal_places=4)
    w = models.DecimalField(max_digits=8, decimal_places=4)
    h = models.DecimalField(max_digits=8, decimal_places=4)

    camera_roi = models.ForeignKey(CameraROI, on_delete=models.CASCADE)


class CameraMotionDetected(models.Model):
    class Meta:
        unique_together = ['event_ref', 'is_motion']

    created_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.PROTECT)
    in_rectangle_roi = models.ManyToManyField(CameraRectangleROI, blank=True)

    event_ref = models.UUIDField()
    is_motion = models.BooleanField()


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
    class Meta:
        unique_together = ['event_ref', 'is_motion']

    created_at = models.DateTimeField(auto_now_add=True)
    picture = models.ImageField(blank=True, null=True)
    device = models.ForeignKey(Device, on_delete=models.PROTECT)

    event_ref = models.UUIDField()
    is_motion = models.BooleanField()
