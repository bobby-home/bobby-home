from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers
from . import views
from django.conf import settings

router = routers.SimpleRouter()
router.register(r'location', views.LocationsViewSet)
router.register(r'attachment', views.AttachmentViewSet)
router.register(r'alert', views.AlertViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
