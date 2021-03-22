from django.views.generic import CreateView

from house.models import House
from utils.django.forms import ChangeForm


class HouseCreateView(ChangeForm, CreateView):
    model = House
    fields = '__all__'
