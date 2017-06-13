from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
import uuid


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    uid = models.CharField(max_length=32, unique=True)
    telegram_chat_id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, **kwargs):
    try:
        instance.profile
    except Profile.DoesNotExist:
        sender.profile = Profile.objects.create(user=instance, uid=uuid.uuid4().hex)
