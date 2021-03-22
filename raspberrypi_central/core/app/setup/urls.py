from django.urls import path

from account.views import SignUpView
from setup.steps import STEPS
from setup.views import setup_view

app_name = 'setup'

step_urls = []
for step in STEPS:
    next_path = f'/setup?validated_step={step.slug}'
    step_urls.append(path(step.slug, step.view.as_view(success_url=next_path, extra_context={'next': next_path}), name=f'{step.slug}'))

urlpatterns = [
    path('', setup_view),
] + step_urls
