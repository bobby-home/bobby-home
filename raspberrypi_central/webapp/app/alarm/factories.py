import uuid
from datetime import timedelta

import factory
from django.core.files.base import ContentFile
from django.utils import timezone
from faker import Factory

from devices.factories import DeviceFactory
from .models import CameraRectangleROI, AlarmStatus, CameraROI, CameraMotionDetectedPicture, AlarmSchedule

faker = Factory.create()

class AlarmStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = AlarmStatus

    running = True
    device = factory.SubFactory(DeviceFactory)


class AlarmScheduleFactory(factory.DjangoModelFactory):
    class Meta:
        model = AlarmSchedule

    start_time = factory.LazyFunction(timezone.now)
    end_time = factory.LazyAttribute(lambda _: timezone.now() + timedelta(hours=9))

    monday    = factory.Faker('pybool')
    tuesday   = factory.Faker('pybool')
    wednesday = factory.Faker('pybool')
    thursday  = factory.Faker('pybool')
    friday    = factory.Faker('pybool')
    saturday  = factory.Faker('pybool')
    sunday    = factory.Faker('pybool')


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
