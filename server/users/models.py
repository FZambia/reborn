from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from core.models import Dashboard


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, **kwargs):
    try:
        instance.profile
    except Profile.DoesNotExist:
        sender.profile = Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_dashboard(sender, instance, **kwargs):
    if not Dashboard.objects.filter(user=instance, is_default=True).exists():
        Dashboard.objects.create(user=instance, is_default=True)
