from application.settings import get_option

import logging
import requests
import traceback
import requests.exceptions


def send_notifications(entries):
    """
    We don't expect any Exceptions from this function - all exceptions inside
    this func must be catched and logged.
    """
    notify_telegram(entries)


def notify_telegram(entries):
    bot_token = get_option("notifications.telegram.bot_token", "")
    if not bot_token:
        return

    for entry in entries:
        chat_id = entry.subscription.user.profile.telegram_chat_id
        if not chat_id:
            continue

        text = "[{}]({}) ({})".format(entry.title, entry.url, entry.subscription.source)

        data = {
            'chat_id': int(chat_id),
            'text': text,
            'parse_mode': 'Markdown'
        }

        try:
            requests.post(
                'https://api.telegram.org/bot{}/sendMessage'.format(bot_token),
                data=data,
                timeout=3
            )
        except requests.exceptions.RequestException:
            log = logging.getLogger("app")
            log.error('Error sending to Telegram: %s' % (traceback.format_exc()))
