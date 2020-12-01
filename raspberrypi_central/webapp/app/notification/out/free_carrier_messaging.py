from urllib import parse

import requests


class FreeCarrierMessaging:

    def send_message(self, credential, message, *args):
        if message is None:
            return

        data = {
            'user': credential.free_user,
            'pass': credential.free_password,
            'msg': message
        }
        query = parse.urlencode(data)
        url = f'https://smsapi.free-mobile.fr/sendmsg?{query}'

        res = requests.get(url)

        res.raise_for_status()
        # free api
        # errorcodes = {400: 'Missing Parameter',
        #             402: 'Spammer!',
        #             403: 'Access Denied',
        #             500: 'Server Down'}
