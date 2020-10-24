from django.views.generic import CreateView, UpdateView, ListView

from alarm.forms import CameraRectangleROIForm
from alarm.models import CameraRectangleROI


class CameraRectangleROICreate(CreateView):
    template_name = 'alarm/camera_rectangle_roi_form.html'
    model = CameraRectangleROI
    form_class = CameraRectangleROIForm

class CameraRectangleROIUpdate(UpdateView):
    template_name = 'alarm/camera_rectangle_roi_form.html'
    model = CameraRectangleROI
    form_class = CameraRectangleROIForm

class CameraRectangleROIList(ListView):
    queryset = CameraRectangleROI.objects.all()
    template_name = 'alarm/camera_rectangle_roi_list.html'
    context_object_name = 'rois'
