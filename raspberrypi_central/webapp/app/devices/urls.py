from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'location', views.LocationsViewSet)
router.register('attachment', views.AttachmentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
