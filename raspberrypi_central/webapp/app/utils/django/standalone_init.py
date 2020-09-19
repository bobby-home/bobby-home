import os
import sys
import django

def init():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
    django.setup()
