from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
]
