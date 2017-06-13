from django.db import models
from django.utils.translation import ugettext_lazy as _


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
