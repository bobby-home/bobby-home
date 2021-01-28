from django.urls import include, path

from alarm.views.alarm_status_views import AlarmStatusList, AlarmStatusUpdate, AlarmStatusCreate

app_name = 'alarm'

status_patterns = [
    path('', AlarmStatusList.as_view(), name='status-list'),
    path('<int:pk>/edit', AlarmStatusUpdate.as_view(), name='status-edit'),
    path('add', AlarmStatusCreate.as_view(), name='status-add')
]

urlpatterns = [
    path('status/', include(status_patterns)),
]
