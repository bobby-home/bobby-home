import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from devices.models import Device, DeviceType

FILE = './data/new_devices'

if os.path.isfile(FILE):
    with open(FILE) as new_devices:
        for new_device in new_devices: 
            data = new_device.split('/')

            device_id = data[0]
            device_ip = data[1]
            device_type = data[2]

            obj, created = DeviceType.objects.get_or_create(
                type=device_type,
                defaults={'type': device_type},
            )

            Device(device_id=device_id, device_type=obj)
        
        os.remove(FILE)
