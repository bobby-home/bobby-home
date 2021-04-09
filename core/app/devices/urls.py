from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import include, path
from django.views.generic import DetailView
from devices.models import Device

app_name = 'device'

class DeviceCameraMotions(LoginRequiredMixin, DetailView):
    model = Device
    template_name = 'device/device_camera_motion_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

urlpatterns = [
    path('<int:pk>/camera/motions', DeviceCameraMotions.as_view(), name='camera-motion-list')
]
