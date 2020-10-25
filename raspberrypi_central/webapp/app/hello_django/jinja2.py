# from: https://docs.djangoproject.com/en/3.0/topics/templates/#module-django.template.backends.django
from django.urls import reverse
from jinja2 import Environment
from django.templatetags.static import static


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
    })
    return env
