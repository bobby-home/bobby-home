from alarm_requests import AlarmRequests
import os
import asyncio
import logging


api_key = os.environ['API_KEY']
api_url = os.environ['API_URL']
device_id = os.environ['DEVICE_ID']

def loop_exception_handler(loop, context):
    logging.error(f"Caught exception : {context['exception']}")

def notify_motion():
    reqs = AlarmRequests(api_key, api_url, device_id)

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(loop_exception_handler)

    print('run even loop tasks')
    future = asyncio.ensure_future(reqs.send_all())
    loop.run_until_complete(future)
    print('done even loop')

notify_motion()
