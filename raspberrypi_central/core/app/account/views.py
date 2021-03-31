from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

# @TODO see #159
from account.models import Account

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ('first_name','last_name','email',)

class SignUpView(generic.CreateView):
    # model = Account
    # fields = '__all__'
    form_class = CustomUserCreationForm
    # success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def clean(self):
        self.cleaned_data['is_staff'] = True
        self.cleaned_data['is_superuser'] = True
        self.cleaned_data['is_admin'] = True

    def form_valid(self, form):
        form.cleaned_data['password'] = form.cleaned_data['password1']

        # used for data validation, not saved in db.
        form.cleaned_data.pop('password1', None)
        form.cleaned_data.pop('password2', None)

        self.object = Account.objects.create_superuser(**form.cleaned_data)

        return HttpResponseRedirect(self.get_success_url())
