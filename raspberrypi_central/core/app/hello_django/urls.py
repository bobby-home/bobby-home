from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

from hello_django.views import HomeView, ConfigurationView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path(r'admin/', admin.site.urls),
    path('device/', include('devices.urls')),
    path('alarm/', include('alarm.urls', namespace='alarm')),
    path('camera/', include('camera.urls', namespace='camera')),
    path('accounts/', include('account.urls')),
    path('setup/', include('setup.urls', namespace='setup')),
    path('configuration/', ConfigurationView.as_view(), name='configuration'),
    path('house/', include('house.urls', namespace='house')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

    # https://docs.djangoproject.com/en/3.0/howto/static-files/#serving-files-uploaded-by-a-user-during-development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
