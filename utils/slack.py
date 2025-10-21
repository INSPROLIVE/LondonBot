# utils/slack.py
import requests
import logging
from typing import Optional

logger = logging.getLogger('slack')

def post_slack_webhook(webhook_url: str, text: str, channel: Optional[str]=None, username: Optional[str]=None):
    """Post a simple text message to a Slack incoming webhook.

    webhook_url: full incoming webhook URL (https://hooks.slack.com/services/...)
    text: message text
    channel, username: optional override fields
    """
    if not webhook_url:
        logger.debug('No slack webhook configured')
        return False
    payload = { 'text': text }
    if channel:
        payload['channel'] = channel
    if username:
        payload['username'] = username
    try:
        r = requests.post(webhook_url, json=payload, timeout=5)
        if r.status_code != 200:
            logger.warning(f"Slack webhook returned {r.status_code}: {r.text}")
            return False
        return True
    except Exception as e:
        logger.exception('Failed to post to Slack webhook')
        return False
