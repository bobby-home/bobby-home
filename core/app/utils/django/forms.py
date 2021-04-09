from django.views.generic import CreateView
from django.utils.translation import gettext as _


class ChangeForm:
    """
    Class to render a form.
    """
    template_name = 'generics/_change_form.html'

    def get_context_data(self, **kwargs):
        old_context = super().get_context_data(**kwargs)

        model = self.model
        opts = model._meta

        add = self.object is None

        if add:
            title = _('Add %s')
        else:
            title = _('Change %s')
        # elif self.has_change_permission(request, obj):
        #     title = _('Change %s')
        # else:
        #     title = _('View %s')

        context = {
            **old_context,
            'title': title % opts.verbose_name,
        }

        return context
