from urllib import request, parse
import asyncio
import os
from functools import partial
import aiohttp
from aiohttp import ClientSession
from typing import IO


"""FREE MOBILE SMS NOTIFICATION

Send SMS notifications to your cell phone with the Free Mobile's new service.
Enable it on your user account page and get your credentials !
"""

USER = os.environ['FREE_USER']
PASSWORD = os.environ['FREE_PASSWORD']


async def send_sms(user: str, password: str, message: str):
    data = {'user': user, 'pass': password, 'msg': message}
    query = parse.urlencode(data)
    url = 'https://smsapi.free-mobile.fr/sendmsg?{}'.format(query)

    errorcodes = {400: 'Missing Parameter',
                  402: 'Spammer!',
                  403: 'Access Denied',
                  500: 'Server Down'}

    async with ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()

async def get_session() -> ClientSession:
    async with ClientSession() as session:
        return session


async def main():
    # session = await get_session()
    sms = partial(send_sms, USER, PASSWORD)
    await sms('Hello World !')
    return 0
 
if __name__ == '__main__':
    asyncio.run(main())
