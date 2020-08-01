from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from alarm.views import AlarmView, AlarmStatusViewSet

router = routers.SimpleRouter()
router.register(r'alarm_status', AlarmStatusViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('', AlarmView.as_view()),
]
