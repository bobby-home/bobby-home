# Alarm

## Schedule
The resident has the possibility to schedule when the system alarm is on or off.

- `AlarmSchedule` model, allows the resident to schedule it based on hour/minute and days.
    - Ex: I want my alarm to be on from 8am to 4pm every monday, tuesday... Outside of this range, the alarm is off.
- `AlarmScheduleDateRange` model, allows the resident to shecule it based on datetime range.
    - Ex: I go on holiday from 2 august 8am to 5 august 4pm, please let the alarm on.
    - We pause all the `AlarmSchedule` during this time range.

### Technically
To schedule things, we're using Celery task scheduled with Celery beat configured by [Django celery beat](https://github.com/celery/django-celery-beat) (allows configuration to be backed by Django ORM).


When we want to turn on/off the alarm, we have to schedule two tasks:
- One task to turn on
- One task to turn off

That's why we do have two `OneToOne` relationship fields in these models.

### Danger zone
:warning: We can't use **bulk operations**. For instance, we are using the `delete` method on model, and this method isn't called when we do bulk operations.

Django celery beat needs to know when an operation is done on a schedule. They can't know on bulk operations, we have to tell that something changed, so schedule are written.

So, bulk operations are error prone. That is why we have decided to no use it. We can't have performance issues here because schedules won't have millions of rows, it will be at the most 10-20 rows.

