import uuid

import factory
from django.core.files.base import ContentFile
from faker import Factory

from devices.factories import DeviceFactory
from .models import CameraRectangleROI, AlarmStatus, CameraROI, CameraMotionDetectedPicture

faker = Factory.create()


class CameraMotionDetectedPictureFactory(factory.DjangoModelFactory):
    class Meta:
        model = CameraMotionDetectedPicture

    event_ref = factory.LazyAttribute(lambda obj: uuid.uuid4().__str__())
    is_motion = True
    device = factory.SubFactory(DeviceFactory)
    picture = factory.django.FileField()


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


class AlarmStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = AlarmStatus

    running = True
    device = factory.SubFactory(DeviceFactory)
