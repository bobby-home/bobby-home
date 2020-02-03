from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'location', views.LocationsViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
