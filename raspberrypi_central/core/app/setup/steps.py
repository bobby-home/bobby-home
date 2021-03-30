from dataclasses import dataclass
from typing import Type, Optional

from django.views import View

from account.views import SignUpView
from house.views import HouseCreateView
from setup.views import SetupDoneView, MainDeviceLocationView, TelegramBotView, TelegramBotStartView, \
    MainDeviceAlarmView
from django.contrib.auth import views as auth_views

@dataclass
class Step:
    slug: str
    view: Type[View]

create_account_step = Step(
    slug='create_account',
    view=SignUpView
)

login_account_step = Step(
    slug='login',
    view=auth_views.LoginView
)

house_timezone = Step(
    slug='house',
    view=HouseCreateView
)

main_device_location = Step(
    slug='device_location',
    view=MainDeviceLocationView,
)

main_device_alarm = Step(
    slug='main_alarm',
    view=MainDeviceAlarmView,
)

telegram_bot_step = Step(
    slug='telegram_bot',
    view=TelegramBotView
)


telegram_bot_start = Step(
    slug='telegram_bot_start',
    view=TelegramBotStartView
)

done_step = Step(
    slug='done',
    view=SetupDoneView
)

STEPS = [
    create_account_step,
    login_account_step,
    house_timezone,
    main_device_location,
    main_device_alarm,
    telegram_bot_step,
    telegram_bot_start,
    done_step,
]

def get_step(slug: str) -> Optional[Step]:
    for step in STEPS:
        if step.slug == slug:
            return step


def get_current_step(last_slug: str) -> Optional[Step]:
    for i, step in enumerate(STEPS):
        if step.slug == last_slug:
            if i+1 == len(STEPS):
                return step

            return STEPS[i+1]
