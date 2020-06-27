from devices.api.views import DeviceViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'devices'

router = DefaultRouter()
router.register(r'device', DeviceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
