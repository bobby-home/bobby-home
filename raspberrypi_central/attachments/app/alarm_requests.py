# Make a post request to create an alert without attachment in the first time.

import os
from urllib.parse import urljoin
from typing import IO
from aiohttp import ClientSession
from urllib import request, parse
import asyncio

api_endpoint = os.environ['API_SEND_ALERT_ENDPOINT']

USER = os.environ['FREE_USER']
PASSWORD = os.environ['FREE_PASSWORD']


class AlarmRequests():
    def __init__(self, api_key: str, api_url: str, device_id: str):
        self.api_key = api_key
        self.device_id = device_id
        self.api_url = api_url


    async def _send_alert(self, session: ClientSession, api_endpoint: str):
        headers = {'API-KEY': self.api_key,}

        payload = {'devices': [self.device_id], 'alert_type': 'motion', 'severity': 'high' }
        full_url = urljoin(self.api_url, api_endpoint)

        async with session.post(full_url, data=payload, headers=headers) as response:
            response.raise_for_status()


    """FREE MOBILE SMS NOTIFICATION

    Send SMS notifications to your cell phone with the Free Mobile's new service.
    Enable it on your user account page and get your credentials !
    """
    async def _send_sms(self, session: ClientSession, user: str, password: str, message: str):
        data = {'user': user, 'pass': password, 'msg': message}
        query = parse.urlencode(data)
        url = 'https://smsapi.free-mobile.fr/sendmsg?{}'.format(query)

        # errorcodes = {400: 'Missing Parameter',
        #             402: 'Spammer!',
        #             403: 'Access Denied',
        #             500: 'Server Down'}

        async with session.get(url) as resp:
            resp.raise_for_status()

    async def send_all(self):
        async with ClientSession() as session:
            send_sms_task = asyncio.create_task(self._send_sms(session, USER, PASSWORD, 'Une intrusion a été détectée !'))

            # without return_exceptions, exceptions go to the global handler.
            # but doesn't work for me here, if it goes to the global handler it doesn't catch it and let the program crashed
            # so if send_alert_task crashes, all the others are not executed, that is BAD!
            # @TODO research why it does that.
            return await asyncio.gather(asyncio.ensure_future(self._send_alert(session, api_endpoint)), send_sms_task)

            # if isinstance(alerted, Exception):
            #     print("couldn't create the alert.")
