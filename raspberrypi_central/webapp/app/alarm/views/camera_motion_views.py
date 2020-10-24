from django.views.generic import ListView

from alarm.models import CameraMotionDetected


class CameraMotionDetectedList(ListView):
    template_name = 'alarm/camera_motion_detected_list.html'
    queryset = CameraMotionDetected.objects.order_by('-created_at')
    context_object_name = 'motions'
