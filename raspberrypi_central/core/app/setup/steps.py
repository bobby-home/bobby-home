from dataclasses import dataclass
from typing import Type, Optional

from django.views import View

from account.views import SignUpView
from setup.views import SetupDoneView


@dataclass
class Step:
    slug: str
    view: Type[View]

create_account_step = Step(
    slug='create_account',
    view=SignUpView
)

# house_timezone = Step(
#     slug='house',
#     description=''
# )
#
# main_device_location = Step(
#     slug='device_location',
#     description=''
# )
#
# telegram_bot_step = Step(
#     slug='telegram_bot',
#     description='Some description given to the user'
# )
#
# telegram_bot_start = Step(
#     slug='telegram_bot_start',
#     description=''
# )

done_step = Step(
    slug='done',
    view=SetupDoneView
)

STEPS = [
    create_account_step,
    done_step,
    # house_timezone,
    # main_device_location,
    # telegram_bot_step,
    # telegram_bot_start
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
