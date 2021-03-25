from django.db import IntegrityError
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse

# Create your views here.
from django.urls import reverse
from django.views.generic import TemplateView, CreateView

from devices.models import Device
from house.models import Location, TelegramBot, TelegramBotStart
from notification.models import UserTelegramBotChatId
from setup.models import StepDone
from utils.django.forms import ChangeForm


def setup_view(request: HttpRequest) -> HttpResponse:
    """
    Redirect to step to do/validate.
    Register the progress thanks to the querystring `?validated_step={step_slug}`.

    Parameters
    ----------
    request : HttpRequest

    Returns
    -------
    HttpResponse
    """
    from setup.steps import STEPS, get_current_step, get_step

    validated_step_slug = request.GET.get('validated_step', None)

    if validated_step_slug:
        validated_step = get_step(validated_step_slug)
        if validated_step:
            try:
                StepDone.objects.create(slug=validated_step.slug)
            except IntegrityError:
                # the step has already been marked as done.
                pass

    try:
        last_step = StepDone.objects.latest()
        current_step = get_current_step(last_step.slug)
    except StepDone.DoesNotExist:
        current_step = STEPS[0]

    return redirect(reverse(f'setup:{current_step.slug}'))

class SetupDoneView(TemplateView):
    # not used but its needed because setup inject `success_url` in every step view.
    # otherwise: TypeError: SetupDoneView() received an invalid keyword 'success_url'. as_view only accepts arguments that are already attributes of the class.
    success_url = ''
    template_name = 'setup/done.html'


class TelegramBotView(ChangeForm, CreateView):
    model = TelegramBot
    fields = '__all__'
    template_name = 'setup/telegrambot_form.html'

class TelegramBotStartView(ChangeForm, CreateView):
    model = UserTelegramBotChatId
    fields = '__all__'
    template_name = 'setup/telegrambotstart_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['starts'] = TelegramBotStart.objects.all()
        return context


class MainDeviceLocationView(ChangeForm, CreateView):
    model = Location
    fields = '__all__'
    template_name = 'setup/location_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_device'] = Device.objects.main_device()

        return context

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)

        main_device = Device.objects.main_device()
        main_device.location = self.object
        main_device.save()

        return response

    def get_initial(self):
        initial = super().get_initial()
        # update initial field defaults with custom set default values:
        # initial.update({'charfield1': 'foo', 'charfield2': 'bar'})
        return initial
