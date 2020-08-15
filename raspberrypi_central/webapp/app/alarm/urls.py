from django.urls import include, path
from alarm.views import AlarmView


urlpatterns = [
    # path('', include(router.urls)),
    path('', AlarmView.as_view()),
]
