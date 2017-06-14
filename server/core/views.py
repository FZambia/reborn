# coding: utf-8
from django.db import IntegrityError
from django.utils import timezone

from social_django.utils import load_backend, load_strategy
from rest_framework.authtoken.models import Token
from rest_framework import parsers
from rest_framework import renderers
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework import exceptions
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response

from core.models import Category, Provider, Loader, Subscription, Entry
import core.serializers as serializers
from core.notifications import send_notifications


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'paginate_by'
    max_page_size = 100


def register_by_access_token(request, backend):
    strategy = load_strategy(request)
    backend = load_backend(strategy, backend, "")
    access_token = request.data.get("access_token")
    user = backend.do_auth(access_token)
    return user


class ObtainAuthToken(APIView):
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    model = Token

    def post(self, request, backend):
        user = register_by_access_token(request, backend)
        if user and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': token.key,
                'backend': backend
            })
        else:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)


class ReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class ProviderViewSet(viewsets.ModelViewSet):

    queryset = Provider.objects.all()
    serializer_class = serializers.ProviderSerializer
    permission_classes = (ReadOnlyPermission, )


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        # To not perform the csrf check.
        return


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        qs = super(CategoryViewSet, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class SubscriptionViewSet(viewsets.ModelViewSet):

    queryset = Subscription.objects.all()
    serializer_class = serializers.SubscriptionSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        qs = super(SubscriptionViewSet, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class EntryViewSet(viewsets.ModelViewSet):

    queryset = Entry.objects.all()
    serializer_class = serializers.EntrySerializer
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = CustomPageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('subscription',)

    def get_queryset(self):
        qs = super(EntryViewSet, self).get_queryset()
        qs = qs.filter(subscription__user=self.request.user)
        if "category" in self.request.query_params:
            qs = qs.filter(subscription__categories=self.request.query_params["category"])
        if "search" in self.request.query_params:
            qs = qs.filter(title__icontains=self.request.query_params["search"])
        if "favorite" in self.request.query_params:
            qs = qs.filter(is_favorite=True)
        return qs

    def list(self, request, *args, **kwargs):
        return super(EntryViewSet, self).list(request, *args, **kwargs)


class LoaderAuthentication(TokenAuthentication):

    model = Loader

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


class IsLoaderAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.auth


class SourceListView(APIView):

    authentication_classes = (LoaderAuthentication, )
    permission_classes = (IsLoaderAuthenticated, )

    def get(self, request, *args, **kwargs):
        provider = request.auth.provider
        sources = Subscription.objects.filter(
            provider=provider).values_list('source', flat=True).distinct()
        return Response(sources)


class UploadException(Exception):
    pass


class UploadView(APIView):

    authentication_classes = (LoaderAuthentication, )
    permission_classes = (IsLoaderAuthenticated, )

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
        provider=provider, source=source, score__lte=score
    )

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
