from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'alarm_status', views.AlarmStatusViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('', views.index, name='index'),
]
