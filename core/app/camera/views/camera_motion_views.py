import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from camera.models import CameraMotionDetected, CameraMotionDetectedPicture
from utils.json.encoders import DecimalEncoder


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
        context['json_camera_roi'] = json.dumps(camera_roi, cls=DecimalEncoder)

        bounding_boxes = camera_motion_detected.cameramotiondetectedboundingbox_set.all()
        bounding_boxes_plain = list(bounding_boxes.values())
        context['bounding_boxes'] = bounding_boxes
        context['json_bounding_boxes'] = json.dumps(bounding_boxes_plain, cls=DecimalEncoder)

        try:
            context['picture'] = CameraMotionDetectedPicture.objects.get(event_ref=camera_motion_detected.event_ref)
        except CameraMotionDetectedPicture.DoesNotExist:
            context['picture'] = None

        return context
