import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from camera.models import CameraMotionDetected, CameraMotionDetectedPicture
from utils.json.decimal_encoder import DecimalEncoder


class CameraMotionDetectedList(LoginRequiredMixin, ListView):
    template_name = 'camera/camera_motion_detected_list.html'
    queryset = CameraMotionDetected.objects.order_by('-motion_started_at')
    context_object_name = 'motions'


class CameraMotionDetectedDetail(LoginRequiredMixin, DetailView):
    model = CameraMotionDetected
    template_name = 'camera/camera_motion_detected_detail.html'
    context_object_name = 'motion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camera_motion_detected: CameraMotionDetected = context[self.context_object_name]

        camera_roi = list(camera_motion_detected.in_rectangle_roi.all().values())

        bounding_boxes = list(camera_motion_detected.cameramotiondetectedboundingbox_set.all().values())
        context['bounding_boxes'] = json.dumps(bounding_boxes, cls=DecimalEncoder)
        context['camera_roi'] = json.dumps(camera_roi, cls=DecimalEncoder)

        try:
            context['picture'] = CameraMotionDetectedPicture.objects.get(event_ref=camera_motion_detected.event_ref, is_motion=False)
        except CameraMotionDetectedPicture.DoesNotExist:
            context['picture'] = CameraMotionDetectedPicture.objects.get(event_ref=camera_motion_detected.event_ref, is_motion=True)
        except CameraMotionDetectedPicture.DoesNotExist:
            context['picture'] = None

        return context
