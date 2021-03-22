from django.db import IntegrityError
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse

# Create your views here.
from django.urls import reverse
from django.views.generic import TemplateView

from setup.models import StepDone


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

