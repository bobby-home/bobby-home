import json

from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView
from django.views.generic.edit import FormView, DeleteView
from django.forms.models import model_to_dict

from alarm.communication.alarm import NotifyAlarmStatus, notify_alarm_status_factory
from alarm.forms import CameraRectangleROIFormSet, CameraROIForm, CameraROIUpdateForm
from alarm.models import CameraRectangleROI, CameraMotionDetectedPicture, CameraROI
from utils.django.json_view import JsonableResponseMixin
from utils.json.decimal_encoder import DecimalEncoder
from utils.mqtt import mqtt_factory


class CameraROIList(ListView):
    queryset = CameraROI.objects.all()
    template_name = 'alarm/camera_roi_list.html'
    context_object_name = 'rois'


def notify_mqtt(device_id, rectangle_rois):
    notify_alarm_status_factory().publish_roi_changed(device_id, rectangle_rois)


class CameraROIDelete(DeleteView):
    model = CameraROI
    success_url = reverse_lazy('alarm:camera_roi-list')


    def delete(self, request, *args, **kwargs):
        camera_roi = self.get_object()
        notify_alarm_status_factory().publish_roi_changed(camera_roi.device_id, None)

        return super().delete(request, *args, **kwargs)


class CameraROIUpdate(JsonableResponseMixin, UpdateView):
    template_name = 'alarm/camera_roi_form.html'
    model = CameraROI
    form_class = CameraROIUpdateForm
    success_url = reverse_lazy('alarm:camera_roi-list')

    # def get_object(self, queryset=None):
    #     print(f'querset = {queryset}')
    #
    #     if queryset is None:
    #         queryset = self.get_queryset()
    #
    #     pk = self.kwargs.get(self.pk_url_kwarg)
    #
    #     try:
    #         # Get the single item from the filtered queryset
    #         obj = queryset.get(pk=pk)
    #     except queryset.model.DoesNotExist:
    #         raise Http404(_("No %(verbose_name)s found matching the query") %
    #                       {'verbose_name': queryset.model._meta.verbose_name})
    #
    #     return obj

    def get_context_data(self, **kwargs):
        context = super(CameraROIUpdate, self).get_context_data(**kwargs)
        camera_roi = context['cameraroi']

        camera_roi_rectangles = list(CameraRectangleROI.objects.filter(camera_roi=camera_roi).values())
        camera_roi_rectangles = json.dumps(camera_roi_rectangles, cls=DecimalEncoder)

        context['camera_rectangle_roi_formset'] = CameraRectangleROIFormSet(queryset=CameraRectangleROI.objects.none())

        context['camera_roi_rectangles'] = camera_roi_rectangles

        motion_picture = CameraMotionDetectedPicture.objects.last()
        context['motion_picture'] = motion_picture.picture

        return context

    def form_valid(self, form): 
        formset = CameraRectangleROIFormSet(self.request.POST)

        if formset.is_valid():
            with transaction.atomic():
                form.save(commit=False)

                camera_roi_pk = form.instance.pk
                # The UI doesn't allow the user to modify a Rectangle. So we delete them all to recreate them.
                CameraRectangleROI.objects.filter(camera_roi=camera_roi_pk).delete()

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.camera_roi_id = camera_roi_pk

                formset.save()
                form.save()

            rectangles = [model_to_dict(instance) for instance in instances]
            transaction.on_commit(lambda: notify_mqtt(form.instance.device_id, rectangles))

            return super().form_valid(form)

        print('no valid, what do we do here :)')
        return super().form_invalid(formset.errors)



class CameraROICreate(FormView):
    template_name = 'alarm/camera_roi_form.html'
    model = CameraROI
    form_class = CameraROIForm
    success_url = reverse_lazy('alarm:camera_roi-list')


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

        if formset.is_valid():
            with transaction.atomic():
                form.save()
                camera_roi_pk = form.instance.pk

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.camera_roi_id = camera_roi_pk

                formset.save()

            rectangles = [model_to_dict(instance) for instance in instances]
            transaction.on_commit(lambda: notify_mqtt(form.instance.device_id, rectangles))

            return super().form_valid(form)


        print('no valid, what do we do here :)')
        return super().form_invalid(formset.errors)


# class CameraRectangleROICreate(CreateView):
#     model = CameraRectangleROI
#     form_class = CameraRectangleROIForm


# class CameraRectangleROIUpdate(UpdateView):
#     template_name = 'alarm/camera_roi_form.html'
#     model = CameraRectangleROI
#     form_class = CameraRectangleROIForm
#
#
# class CameraRectangleROIList(ListView):
#     queryset = CameraRectangleROI.objects.all()
#     template_name = 'alarm/camera_roi_list.html'
#     context_object_name = 'rois'