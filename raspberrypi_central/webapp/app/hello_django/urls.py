from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('device/', include('devices.urls')),
    path('alarm/', include('alarm.urls', namespace='alarm')),
    path('alert/', include('alerts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
#     # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
