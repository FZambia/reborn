from django.db import IntegrityError
from django.utils import timezone

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from rest_framework import status
from rest_framework.response import Response

from core.models import Subscription, Entry
from core.notifications import send_notifications
from loaders.models import RemoteLoader


class RemoteLoaderAuthentication(TokenAuthentication):

    model = RemoteLoader

    def authenticate_credentials(self, key):
        try:
            loader = self.model.objects.select_related('provider').get(token=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not loader.is_active:
            raise exceptions.AuthenticationFailed('Loader inactive or deleted')

        return None, loader

    def authenticate_header(self, request):
        return 'Token'


class IsRemoteLoaderAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.auth


class SourceView(APIView):

    authentication_classes = (RemoteLoaderAuthentication, )
    permission_classes = (IsRemoteLoaderAuthenticated, )

    def get(self, request, *args, **kwargs):
        provider = request.auth.provider
        sources = Subscription.objects.filter(
            source__provider=provider
        ).values_list('source__name', flat=True).distinct()
        return Response(sources)


class UploadException(Exception):
    pass


class UploadView(APIView):

    authentication_classes = (RemoteLoaderAuthentication, )
    permission_classes = (IsRemoteLoaderAuthenticated, )

    def post(self, request, *args, **kwargs):
        provider = request.auth.provider
        data = request.data
        if not isinstance(data, dict):
            raise exceptions.ValidationError('data must be object')

        sources_data = data.get("sources")
        if not isinstance(sources_data, list):
            raise exceptions.ValidationError('sources must be array')

        process_sources_data(provider, sources_data)
        provider.checked_at = timezone.now()
        provider.save()

        return Response({}, status=status.HTTP_200_OK)


def create_entry(provider, source, entry):
    """
    Returns Entry instance in case it was created and None otherwise.
    """
    title = entry.get("title")
    url = entry.get("url")
    permalink = entry.get("permalink")
    content = entry.get("content")
    score = entry.get("score")
    digest = entry.get("digest") or Entry.generate_digest(title, url, permalink, content)
    subscriptions = Subscription.objects.select_related('user', 'user__profile').filter(
        provider=provider, source=source, score__lte=score)

    for subscription in subscriptions:
        try:
            entry, created = Entry.objects.get_or_create(
                subscription=subscription,
                digest=digest,
                defaults={
                    'title': title,
                    'url': url,
                    'permalink': permalink,
                    'content': content,
                }
            )
            entry.score = score
            entry.save()
        except IntegrityError:
            # already saved for this subscription
            return None
        else:
            if created:
                return entry

    return None


def process_sources_data(provider, sources_data):
    entries_created = []
    for source_object in sources_data:
        source = source_object.get("source")
        entries = source_object.get("entries")
        if not isinstance(source, str):
            continue
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                raise UploadException("entry must be object")

            created_entry = create_entry(provider, source, entry)
            if created_entry:
                entries_created.append(created_entry)

    if entries_created:
        send_notifications(entries_created)
