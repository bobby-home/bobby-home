import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from devices.models import Device, DeviceType

device_type = os.environ['DEVICE_MODEL']
device_id = os.environ['DEVICE_ID']

i_device_type, created_type = DeviceType.objects.get_or_create(
    type=device_type,
    defaults={'type': device_type},
)

device, created_device = Device.objects.get_or_create(
    device_id=device_id,
    defaults={
        'device_id': device_id,
        'device_type': i_device_type,
        'is_main': True,
        'name': 'Main device',
    }
)

if created_device:
    print(f'Created device {device} and run on this device.')
else:
    print(f'Run on device {device}')
