from core import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as authtoken_views

router = DefaultRouter()

router.register(r'category', views.CategoryViewSet)
router.register(r'subscription', views.SubscriptionViewSet)
router.register(r'entry', views.EntryViewSet)

urlpatterns = [
    url(r'^v1/', include(router.urls)),
    url(r'^v1/api-token-auth/$', authtoken_views.obtain_auth_token),
    url(r'^v1/api-token-auth/(?P<backend>[^/]+)/$', views.ObtainAuthToken.as_view())
]
