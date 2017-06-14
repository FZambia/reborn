# coding: utf-8
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from core.models import Provider


class RemoteLoader(models.Model):
    """
    RemoteLoader loads content from provider resource.
    """
    name = models.CharField(max_length=64)
    token = models.CharField(max_length=128, blank=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("remote loader")
        verbose_name_plural = _("remote loaders")

    def save(self, **kwargs):
        if not self.pk and not self.token:
            self.token = uuid.uuid4().hex
        super().save(**kwargs)

    def __str__(self):
        return self.name
