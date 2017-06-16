from django.db import models
from django.utils.translation import ugettext_lazy as _
from core.models import Dashboard
from django.db.models.signals import post_save
from django.dispatch import receiver


class KeyValue(models.Model):
    key = models.CharField(max_length=32, unique=True)
    value = models.TextField(blank=True)

    class Meta:
        verbose_name = _("key-value pair")
        verbose_name_plural = _("key-value pairs")

    def __str__(self):
        return self.key

    @classmethod
    def set(cls, key, value):
        entry, _ = cls.objects.get_or_create(key=key)
        entry.value = value
        entry.save()

    @classmethod
    def get(cls, key, default=None):
        try:
            entry = cls.objects.get(key=key)
        except cls.DoesNotExist:
            return default
        else:
            return entry.value


class DashboardNotificationProfile(models.Model):
    dashboard = models.OneToOneField(Dashboard, related_name="notification_profile")
    telegram_chat_id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        verbose_name = _("dashboard notification")
        verbose_name_plural = _("dashboard notifications")

    def __str__(self):
        return self.dashboard


@receiver(post_save, sender=DashboardNotificationProfile)
def create_dashboard_notification_profile(sender, instance, **kwargs):
    try:
        instance.notification_profile
    except DashboardNotificationProfile.DoesNotExist:
        DashboardNotificationProfile.objects.create(dashboard=instance)
