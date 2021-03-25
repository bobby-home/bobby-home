from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from house.models import House
from utils.django.forms import ChangeForm


class HouseCreateView(LoginRequiredMixin, ChangeForm, CreateView):
    model = House
    fields = '__all__'
