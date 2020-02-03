from urllib import request, parse
import os
from functools import partial


"""FREE MOBILE SMS NOTIFICATION

Send SMS notifications to your cell phone with the Free Mobile's new service.
Enable it on your user account page and get your credentials !
"""

USER = os.environ['FREE_USER']
PASSWORD = os.environ['FREE_PASSWORD']


def send_sms(user, password, message):
    data = {'user': user, 'pass': password, 'msg': message}
    query = parse.urlencode(data)
    url = 'https://smsapi.free-mobile.fr/sendmsg?{}'.format(query)

    errorcodes = {400: 'Missing Parameter',
                  402: 'Spammer!',
                  403: 'Access Denied',
                  500: 'Server Down'}
   
    try:
        request.urlopen(url)
        return True, 'Success'
    
    except request.HTTPError as e:
        raise e
        # return False, errorcodes[e.code]

send_sms = partial(send_sms, USER, PASSWORD)

def main():
    send_sms('Hello World !')
    return 0
 
if __name__ == '__main__':
    main()
