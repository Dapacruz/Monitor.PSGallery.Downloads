#!/usr/bin/env python3.6

'''Track the download count of my Toggl.Functions module'''

import logging
import logging.handlers
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

logging_level = logging.DEBUG
module_name = 'Toggl.Functions'
uri = 'https://www.powershellgallery.com/packages/Toggl.Functions'
script_path = os.path.dirname(os.path.realpath(__file__))
log_path = f'{script_path}/logs/toggl.functions.log'
previous_count_path = f'{script_path}/toggl.functions_count'
slack_webhook_url_path = f'{script_path}/slack_webhook_url'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh_formatter = logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
fh = logging.handlers.RotatingFileHandler(log_path, maxBytes=25000000, backupCount=3)
fh.setLevel(logging.DEBUG)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch_formatter = logging.Formatter('%(message)s')
ch.setLevel(logging_level)
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

if os.path.exists(slack_webhook_url_path):
    logger.debug('Loading Slack webhook URL')
    with open(slack_webhook_url_path, 'r') as f:
        slack_webhook_url = f.read().strip()
        logger.debug(f'slack_webhook_url = {slack_webhook_url}')
else:
    logger.debug('Prompting for Slack webhook URL')
    slack_webhook_url = input('Slack Webhook URL: ')
    logger.debug(f'Slack webhook URL file is missing, promted user.\nslack_webhook_url variable: {slack_webhook_url}')
    with open(slack_webhook_url_path, 'w') as f:
        f.write(slack_webhook_url)

try:
    logger.debug(f'Requesting {uri}')
    request = requests.get(uri)
    logger.debug(f'Request Status Code: {request.status_code}')
except Exception as e:
    logger.critical(f'Web request failed:\n{e}')
    raise

logger.debug('Parsing current count')
soup = BeautifulSoup(request.content, 'html.parser')
current_count = int(re.search('.*?([\d,]+).*', soup.find('ul', class_='list-unstyled ms-Icon-ul').li.h2.text).group(1).replace(',', ''))
if current_count:
    logger.debug(f'current_count = {current_count}')
elif datetime.now().minute == 00:
    try:
        logger.debug('Sending Slack message')
        slack_msg = {
            'text': f'Failed to parse the {module_name} module current download count!',
            'username': 'PowerShell Gallery'
        }
        requests.post(slack_webhook_url, json=slack_msg, headers={'Content-Type': 'application/json'})
    except Exception as e:
        logger.critical(f'Post to Slack failed:\n{e}')
        raise

logger.debug('Loading previous count')
if os.path.exists(previous_count_path):
    with open(previous_count_path, 'r') as f:
        previous_count = int(f.read())
        logger.debug(f'previous_count = {previous_count}')
else:
    previous_count = 0
    logger.debug(f'previous_count file missing, setting to default value.\nprevious_count variable: {previous_count}')

logger.debug('Checking if previous count is less than current count')
if previous_count < current_count:
    try:
        logger.debug('Sending Slack message')
        slack_msg = {
            'text': f'You now have {current_count:,d} downloads of your {module_name} module!',
            'username': 'PowerShell Gallery'
        }
        requests.post(slack_webhook_url, json=slack_msg, headers={'Content-Type': 'application/json'})
    except Exception as e:
        logger.critical(f'Post to Slack failed:\n{e}')
        raise

    logger.debug('Saving current count')
    with open(previous_count_path, 'w') as f:
        f.write(str(current_count))
