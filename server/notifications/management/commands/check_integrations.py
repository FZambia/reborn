from django.core.management.base import BaseCommand
from core.models import Dashboard
from application.settings import get_option
from notifications.models import KeyValue
import requests
import logging
import requests.exceptions
import traceback


class Command(BaseCommand):

    help = "Load from content providers"

    def handle(self, *args, **options):
        if get_option("notifications.telegram.enabled", False):
            check_telegram_integration()


def check_telegram_integration():
    bot_token = get_option("notifications.telegram.bot_token", "")
    if not bot_token:
        return

    url = "https://api.telegram.org/bot{}/getUpdates".format(bot_token)

    key = "telegram_last_update_id"
    value = KeyValue.get(key)
    if value:
        url += "?offset=" + str(int(value) + 1) 

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
            process_telegram_message(message)

        KeyValue.set(key, str(update_id))


def process_telegram_message(message):
    bot_token = get_option("notifications.telegram.bot_token", "")
    text = message.get("text", "")

    if not text.startswith("/start"):
        return

    parts = text.split(" ")
    if len(parts) != 2:
        return

    uid = parts[1]
    chat_id = message["chat"]["id"]

    try:
        dashboard = Dashboard.objects.select_related("user", "notification_profile").get(uid=uid)
    except Dashboard.DoesNotExist:
        return

    dashboard.notification_profile.telegram_chat_id = str(chat_id)
    dashboard.notification_profile.save()

    text = "Integration completed"

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
