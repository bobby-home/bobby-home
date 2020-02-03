from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from . import views


router = routers.SimpleRouter()

router.register(r'attachment', views.AttachmentViewSet)
router.register(r'alert', views.AlertViewSet)
router.register(r'alert_type', views.AlertTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
