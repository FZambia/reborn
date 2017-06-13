import uuid
from hashlib import md5
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# in minutes
DEFAULT_LOAD_INTERVAL = 20


class Provider(models.Model):
    """
    Provider is a resource that provides content (Reddit for example).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    checked_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    load_interval = models.IntegerField(default=DEFAULT_LOAD_INTERVAL, help_text="in minutes")

    class Meta:
        verbose_name = _("provider")
        verbose_name_plural = _("providers")

    def __str__(self):
        return self.name


class Loader(models.Model):
    """
    Loader loads content from provider resource.
    """
    name = models.CharField(max_length=64)
    token = models.CharField(max_length=128, blank=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("loader")
        verbose_name_plural = _("loaders")

    def save(self, **kwargs):
        if not self.pk and not self.token:
            self.token = uuid.uuid4().hex
        super(Loader, self).save(**kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    User defined category for entries.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return u"{0} by {1}".format(self.name, self.user.username)


class Subscription(models.Model):
    """
    User defined subscription to source string from provider.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    provider = models.ForeignKey(Provider)
    source = models.CharField(max_length=100)
    score = models.PositiveIntegerField(default=0)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return u"{0} by {1}".format(self.source, self.user.username)

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
        unique_together = ('user', 'provider', 'source')


class Entry(models.Model):
    """
    Entry for user subscription.
    """
    subscription = models.ForeignKey(Subscription)
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255, blank=True)
    permalink = models.URLField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    digest = models.CharField(max_length=64, blank=True)
    is_favorite = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("entry")
        verbose_name_plural = _("entries")
        unique_together = ('subscription', 'digest')
        ordering = ("-id", )

    @staticmethod
    def generate_digest(*values):
        container = md5()
        for value in values:
            if not value:
                value = ''
            container.update(value.encode('utf-8'))
        return container.hexdigest()
