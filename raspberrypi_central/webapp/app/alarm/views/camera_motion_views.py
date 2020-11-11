from django.views.generic import ListView, DetailView

from alarm.models import CameraMotionDetected, CameraMotionDetectedPicture


class CameraMotionDetectedList(ListView):
    template_name = 'alarm/camera_motion_detected_list.html'
    queryset = CameraMotionDetected.objects.order_by('-created_at')
    context_object_name = 'motions'


class CameraMotionDetectedDetail(DetailView):
    model = CameraMotionDetected
    context_object_name = 'motion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camera_motion_detected: CameraMotionDetected = context[self.context_object_name]
        print(context['object'])

        try:
            context['picture'] = CameraMotionDetectedPicture.objects.get(event_ref=camera_motion_detected.event_ref)
        except CameraMotionDetectedPicture.DoesNotExist:
            context['picture'] = None

        return context
