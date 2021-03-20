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
