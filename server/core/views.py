# coding: utf-8
from social_django.utils import load_backend, load_strategy
from rest_framework.authtoken.models import Token
from rest_framework import parsers
from rest_framework import renderers
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response

from core.models import Category, Provider, Subscription, Entry
import core.serializers as serializers


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
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
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
