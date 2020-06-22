from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('device/', include('devices.urls')),
    path('alarm/', include('alarm.urls')),
    path('alert/', include('alerts.urls')),
]


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),

#         # For django versions before 2.0:
#         # url(r'^__debug__/', include(debug_toolbar.urls)),

#     ] + urlpatterns
#     # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
