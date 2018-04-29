#!/usr/bin/env python3.6

# Track the download count of my VMware.VimAutomation.Custom module

import logging
import os
import requests
from bs4 import BeautifulSoup

uri = 'https://www.powershellgallery.com/packages/VMware.VimAutomation.Custom'
script_path = os.path.dirname(os.path.realpath(__file__))
log_path = f'{script_path}/vmware.vimautomation.custom.log'
previous_count_path = f'{script_path}/vmware.vimautomation.custom_count'
slack_webhook_url_path = f'{script_path}/slack_webhook_url'

logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

if os.path.exists(slack_webhook_url_path):
    with open(slack_webhook_url_path, 'r') as f:
        slack_webhook_url = f.read()
        logging.debug(f'slack_webhook_url variable: {slack_webhook_url}')
else:
    slack_webhook_url = input('Slack Webhook URL: ')
    logging.debug(f'Slack webhook URL file is missing, promted user.\nslack_webhook_url variable: {slack_webhook_url}')
    with open(slack_webhook_url_path, 'w') as f:
        f.write(slack_webhook_url)

request = requests.get(uri)
logging.debug(f'request variable: {request}')
soup = BeautifulSoup(request.content, 'html.parser')
count = int(soup.find('p', class_='stat-number').text)
logging.debug(f'count variable: {count}')

if os.path.exists(previous_count_path):
    with open(previous_count_path, 'r') as f:
        previous_count = int(f.read())
        logging.debug(f'previous_count variable: {previous_count}')
else:
    previous_count = 0
    logging.debug(f'previous_count file missing, setting to default value.\nprevious_count variable: {previous_count}')

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
        msg = f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}'
        logging.warn(msg)
        raise ValueError(msg)

with open(previous_count_path, 'w') as f:
    f.write(str(count))
