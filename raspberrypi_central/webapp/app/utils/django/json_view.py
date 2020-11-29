import json

from django.http import JsonResponse

"""
@TODO: we use self.request.is_ajax() which is deprecated since django 3.1
We should use the self.request.accepts method, but this is not working here.
-> django 'WSGIRequest' object has no attribute 'accepts'
"""

class JsonableResponseMixin:
    """
    Mixin to add JSON support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def post(self, request, *args, **kwargs):
        """
        We parse the body and assign it to the "POST" request property.
        More information: https://stackoverflow.com/a/30879038
        """
        if self.request.is_ajax():
            request.POST = json.loads(request.body)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        response = super().form_invalid(form)

        if not self.request.is_ajax():
        # if self.request.accepts('text/html'):
            return response
        else:
            return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)

        if not self.request.is_ajax():
        # if self.request.accepts('text/html'):
            return response

        data = {
            'pk': self.object.pk,
        }

        return JsonResponse(data)
