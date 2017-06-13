from django.core.management.base import BaseCommand
from users.models import Profile
from application.settings import get_option
import requests
import logging
import requests.exceptions
import traceback
import hmac
from hashlib import sha256


class Command(BaseCommand):

    help = "Load from content providers"

    def handle(self, *args, **options):
        check_telegram_integration()


def generate_integration_token(chat_id):
    secret = get_option("app.secret", "")
    h = hmac.new(secret.encode(), digestmod=sha256)
    h.update(str(chat_id).encode())
    token = h.hexdigest()
    return token


def check_telegram_integration():
    bot_token = get_option("notifications.telegram.bot_token", "")
    if not bot_token:
        return

    url = "https://api.telegram.org/bot{}/getUpdates".format(bot_token)
    try:
        resp = requests.get(url, timeout=5)
    except requests.exceptions.RequestException:
        return

    if resp.status_code != 200:
        return

    try:
        data = resp.json()
    except ValueError:
        return

    if not data.get("ok"):
        return

    for update in data.get("result", []):
        update_id = update["update_id"]
        message = update.get("message")
        if message:
            chat_id = message["chat"]["id"]
            token = generate_integration_token(chat_id)
            confirm_url = "https://google.com/notifications/telegram/finish/?token={}&chat_id={}".format(
                token, chat_id
            )
            text = "Tap on link to finish integration: {}".format(confirm_url)

            data = {
                'chat_id': chat_id,
                'text': text
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
