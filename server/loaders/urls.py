from loaders import views
from django.conf.urls import url


urlpatterns = [
    url(r'^v1/upload/$', views.UploadView.as_view()),
    url(r'^v1/sources/$', views.SourceView.as_view()),
]
