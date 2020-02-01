# Make a post request to create an alert without attachment in the first time.

import requests
import os
from urllib.parse import urljoin

api_key = os.environ['API_KEY']
device_id = os.environ['DEVICE_ID']
api_url = os.environ['API_URL']


s = requests.Session()
s.headers.update({'API-KEY': api_key,})

payload = {'device_id': device_id, 'alert_type': 'motion', 'severity': 2 }

response = s.post(url=urljoin(api_url, 'device/attachment/'), data=payload)
response.raise_for_status()
