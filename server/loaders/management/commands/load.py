from django.core.management.base import BaseCommand
from core.models import Provider, Subscription
from loaders.views import process_sources_data
from loaders.providers.reddit import load as reddit_load
from loaders.providers.hackernews import load as hackernews_load
from datetime import timedelta
from django.utils import timezone


loader_funcs = {
    "reddit": reddit_load,
    "hacker news": hackernews_load,
}


class Command(BaseCommand):

    help = "Load from content providers"

    def handle(self, *args, **options):
        providers = Provider.objects.filter(is_active=True)
        for provider in providers:
            now = timezone.now()
            checked_at = provider.checked_at
            if checked_at and checked_at > now - timedelta(minutes=provider.load_interval):
                # too early for this provider.
                continue
            loader_func = loader_funcs.get(provider.name.lower())
            if not loader_func:
                continue
            sources = Subscription.objects.filter(
                provider=provider
            ).values_list('source', flat=True).distinct()
            sources_data = loader_func(sources)
            process_sources_data(provider, sources_data)
            provider.checked_at = timezone.now()
            provider.save()
