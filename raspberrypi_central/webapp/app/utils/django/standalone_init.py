import os
import sys
import django

def init():
    sys.path.append('/usr/src/app')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
    django.setup()
