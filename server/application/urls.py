from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

import json

from application.settings import get_option
from core.serializers import ProviderSerializer, SubscriptionSerializer, CategorySerializer, DashboardSerializer
from core.models import Provider, Subscription, Category, Dashboard


@require_POST
@csrf_exempt
def logout_user(request):
    logout(request)
    return HttpResponse(json.dumps({}), content_type="application/json")


def init(request):
    user = None
    is_authenticated = request.user.is_authenticated()
    if not is_authenticated:
        auth = TokenAuthentication()
        try:
            result = auth.authenticate(request)
            if result:
                user, _ = result
        except AuthenticationFailed:
            pass
        else:
            if user:
                is_authenticated = True
    else:
        user = request.user

    context = {
        "title": "Reborn",
        "is_authenticated": is_authenticated
    }
    if not is_authenticated:
        context["auth"] = {
            "providers": [
                {
                    "name": "Facebook",
                    "client_id": settings.SOCIAL_AUTH_FACEBOOK_KEY,
                    "redirect_uri": ""
                }
            ]
        }
    else:
        context["telegram_bot_name"] = get_option("notifications.telegram.bot_name", "")
        # Provide initialization data for authenticated user.
        context["providers"] = ProviderSerializer(
            Provider.objects.all(), many=True).data
        context["categories"] = CategorySerializer(
            Category.objects.filter(user=user), many=True).data
        dashboard = Dashboard.objects.get(user=user, is_default=True)
        context["dashboard"] = DashboardSerializer(dashboard).data
        context["subscriptions"] = SubscriptionSerializer(
            Subscription.objects.filter(dashboard=dashboard), many=True).data

    return HttpResponse(json.dumps(context), content_type="application/json")


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/init/', init),
    url(r'^api/v1/logout/', logout_user),
    url(r'^api/', include('core.urls')),
    url(r'^api/', include('loaders.urls')),
]


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
