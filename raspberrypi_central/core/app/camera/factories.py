import uuid

import factory
from django.core.files.base import ContentFile
from django.utils import timezone

from camera.models import CameraMotionDetected, CameraMotionDetectedPicture, CameraROI, CameraRectangleROI
from devices.factories import DeviceFactory


class CameraMotionDetectedFactory(factory.DjangoModelFactory):
    class Meta:
        model = CameraMotionDetected

    event_ref = factory.LazyAttribute(lambda obj: str(uuid.uuid4()))
    motion_started_at = factory.LazyAttribute(lambda obj: timezone.now())
    device = factory.SubFactory(DeviceFactory)


class CameraMotionDetectedPictureFactory(factory.DjangoModelFactory):
    class Meta:
        model = CameraMotionDetectedPicture

    event_ref = factory.LazyAttribute(lambda obj: uuid.uuid4().__str__())
    device = factory.SubFactory(DeviceFactory)

    motion_started_picture = factory.django.FileField()
    motion_ended_picture = factory.django.FileField()


class CameraROIFactoryConf:
    default_image_width = 1024
    default_image_height = 768


class CameraROIFactory(factory.DjangoModelFactory):
    class Meta:
        model = CameraROI

    device = factory.SubFactory(DeviceFactory)
    # Hacky thing from here: https://stackoverflow.com/a/25822090
    define_picture = factory.LazyAttribute(
            lambda _: ContentFile(
                factory.django.ImageField()._make_data(
                    {'width': CameraROIFactoryConf.default_image_width, 'height': CameraROIFactoryConf.default_image_height}
                ), 'example.jpg'
            )
        )


class CameraRectangleROIFactory(factory.DjangoModelFactory):
    class Meta:
        model = CameraRectangleROI

    x = 0
    y = 0
    w = 0
    h = 0

    # camera_roi = factory.SubFactory(CameraROIFactory)
