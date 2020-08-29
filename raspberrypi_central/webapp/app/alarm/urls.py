from django.urls import include, path
from alarm.views import AlarmView, AlarmShapeView


urlpatterns = [
    # path('', include(router.urls)),
    path('', AlarmView.as_view()),
    path('shape/', AlarmShapeView.as_view())
]
