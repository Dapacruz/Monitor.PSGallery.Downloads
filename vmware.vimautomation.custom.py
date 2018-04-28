#!/usr/bin/env python3.6

# Track the download count of my VMware.VimAutomation.Custom module

import os
import requests
from bs4 import BeautifulSoup

uri = 'https://www.powershellgallery.com/packages/VMware.VimAutomation.Custom'
script_path = os.path.dirname(os.path.realpath(__file__))
previous_count_path = f'{script_path}/vmware.vimautomation.custom_count'
slack_webhook_url_path = f'{script_path}/slack_webhook_url'

if os.path.exists(slack_webhook_url_path):
    with open(slack_webhook_url_path, 'r') as f:
        slack_webhook_url = f.read()
else:
    slack_webhook_url = input('Slack Webook: ')
    with open(slack_webhook_url_path, 'w') as f:
        f.write(slack_webhook_url)

request = requests.get(uri)
soup = BeautifulSoup(request.content, 'html.parser')
count = int(soup.find('p', class_='stat-number').text)

if os.path.exists(previous_count_path):
    with open(previous_count_path, 'r') as f:
        previous_count = int(f.read())
else:
    previous_count = 0

if previous_count < count:
    try:
        slack_msg = {
            'text': f'You now have {count} downloads of your VMware.VimAutomation.Custom module!',
            'username': 'Python'
        }
        response = requests.post(
            slack_webhook_url, json=slack_msg, headers={'Content-Type': 'application/json'}
        )
    except:
        raise ValueError(
            f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}'
        )

with open(previous_count_path, 'w') as f:
    f.write(str(count))
