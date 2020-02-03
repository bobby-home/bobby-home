# Make a post request to create an alert without attachment in the first time.

import requests
import os
from urllib.parse import urljoin

api_key = os.environ['API_KEY']
device_id = os.environ['DEVICE_ID']
api_url = os.environ['API_URL']
api_endpoint = os.environ['API_SEND_ALERT_ENDPOINT']

def send_alert():
    s = requests.Session()
    s.headers.update({'API-KEY': api_key,})

    payload = {'devices': [device_id], 'alert_type': 'motion', 'severity': 'high' }

    full_url = urljoin(api_url, api_endpoint)
    response = s.post(full_url, data=payload)
    response.raise_for_status()
    print(response.text)
