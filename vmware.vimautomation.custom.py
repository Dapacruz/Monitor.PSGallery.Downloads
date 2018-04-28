#!/usr/bin/env python3.6

# Track the download count of my VMware.VimAutomation.Custom module

import os
import requests
from bs4 import BeautifulSoup

uri = 'https://www.powershellgallery.com/packages/VMware.VimAutomation.Custom'
script_path = os.path.dirname(os.path.realpath(__file__))
count_path = f'{script_path}/vmware.vimautomation.custom_count'
webhook_path = f'{script_path}/webhook'

with open(webhook_path, 'r') as f:
    webhook = f.read()

request = requests.get(uri)
soup = BeautifulSoup(request.content, 'html.parser')
count = int(soup.find('p', class_='stat-number').text)

with open(count_path, mode='r') as f:
    previous_count = int(f.read())

if previous_count < count:
    try:
        slack_msg = {
            'text': f'You now have {count} downloads of your VMware.VimAutomation.Custom module!',
            'username': 'Python'
        }
        response = requests.post(
            webhook, json=slack_msg, headers={'Content-Type': 'application/json'}
        )
    except:
        raise ValueError(
            f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}'
        )

with open(count_path, mode='w') as f:
    f.write(str(count))
