from django.http import HttpRequest, HttpResponse
import re
from http import HTTPStatus
from setup.models import StepDone


SETUP_MATCHER = re.compile(
    r"^/setup/(?:(?P<step>[\w]+))"
)

class SetupSecurityMiddleware:
    """
    Make sure that a step can be done only one time.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        path = request.path
        match = SETUP_MATCHER.match(path)

        if match:
            groups = match.groupdict()
            step = groups['step']
            if StepDone.objects.filter(slug=step).exists():
                return HttpResponse(status=HTTPStatus.FORBIDDEN)

        response = self.get_response(request)

        return response
