import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView
from django.views.generic.edit import FormView, DeleteView
from django.forms.models import model_to_dict

from camera.forms import CameraROIForm, CameraROIUpdateForm, CameraRectangleROIFormSet
from camera.models import CameraROI, CameraRectangleROI, CameraMotionDetectedPicture
from utils.django.json_view import JsonableResponseMixin
from utils.json.decimal_encoder import DecimalEncoder


def notify_mqtt(device_id, camera_roi: CameraROI, rectangle_rois):
    from alarm.communication.out_alarm import notify_alarm_status_factory
    notify_alarm_status_factory().publish_roi_changed(device_id, camera_roi, rectangle_rois)


class CameraROIList(LoginRequiredMixin, ListView):
    queryset = CameraROI.objects.all()
    template_name = 'camera/camera_roi_list.html'
    context_object_name = 'rois'


class CameraROIDelete(LoginRequiredMixin, DeleteView):
    model = CameraROI
    success_url = reverse_lazy('camera:camera_roi-list')


    def delete(self, request, *args, **kwargs):
        camera_roi = self.get_object()
        from alarm.communication.out_alarm import notify_alarm_status_factory
        notify_alarm_status_factory().publish_roi_changed(camera_roi.device_id, camera_roi=None)

        return super().delete(request, *args, **kwargs)


class CameraROIUpdate(LoginRequiredMixin, JsonableResponseMixin, UpdateView):
    template_name = 'camera/camera_roi_form.html'
    model = CameraROI
    form_class = CameraROIUpdateForm
    success_url = reverse_lazy('camera:camera_roi-list')


    def get_context_data(self, **kwargs):
        context = super(CameraROIUpdate, self).get_context_data(**kwargs)
        camera_roi = context['cameraroi']

        camera_roi_rectangles = list(CameraRectangleROI.actives.filter(camera_roi=camera_roi).values())
        camera_roi_rectangles = json.dumps(camera_roi_rectangles, cls=DecimalEncoder)

        context['camera_rectangle_roi_formset'] = CameraRectangleROIFormSet(queryset=CameraRectangleROI.objects.none())

        context['camera_roi_rectangles'] = camera_roi_rectangles

        motion_picture = CameraMotionDetectedPicture.objects.last()
        context['motion_picture'] = motion_picture.picture

        return context

    def form_valid(self, form):
        formset = CameraRectangleROIFormSet(self.request.POST)

        camera_roi: CameraROI = form.instance

        if formset.is_valid():
            with transaction.atomic():
                form.save(commit=False)

                camera_roi_pk = camera_roi.pk
                CameraRectangleROI.objects.filter(camera_roi=camera_roi_pk, disabled=False).update(disabled=True)

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.camera_roi_id = camera_roi_pk

                formset.save()
                form.save()

            rectangles = [model_to_dict(instance) for instance in instances]
            transaction.on_commit(lambda: notify_mqtt(form.instance.device_id, camera_roi, rectangles))

            return super().form_valid(form)

        # @TODO: form no valid, what do we do?
        return super().form_invalid(formset.errors)



class CameraROICreate(LoginRequiredMixin, JsonableResponseMixin, FormView):
    template_name = 'camera/camera_roi_form.html'
    model = CameraROI
    form_class = CameraROIForm
    success_url = reverse_lazy('camera:camera_roi-list')


    def get_context_data(self, **kwargs):
        context = super(CameraROICreate, self).get_context_data(**kwargs)

        context['camera_rectangle_roi_formset'] = CameraRectangleROIFormSet()

        motion_picture = CameraMotionDetectedPicture.objects.last()
        context['motion_picture'] = motion_picture.picture

        return context


    def form_invalid(self, form):
        return super().form_invalid(form)


    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        formset = CameraRectangleROIFormSet(self.request.POST)

        camera_roi: CameraROI = form.instance

        if formset.is_valid():
            with transaction.atomic():
                motion_picture = CameraMotionDetectedPicture.objects.last()
                form.instance.define_picture = motion_picture.motion_started_picture
                form.save()

                camera_roi_pk = form.instance.pk

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.camera_roi_id = camera_roi_pk

                formset.save()

            rectangles = [model_to_dict(instance) for instance in instances]
            transaction.on_commit(lambda: notify_mqtt(form.instance.device_id, camera_roi, rectangles))

            return super().form_valid(form)

        # @TODO: form no valid, what do we do?
        return super().form_invalid(formset.errors)
