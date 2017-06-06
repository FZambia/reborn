from django.contrib import admin
from loaders.models import RemoteLoader


@admin.register(RemoteLoader)
class RemoteLoaderAdmin(admin.ModelAdmin):

    list_display = ('name', 'token', 'is_active')
    search_fields = ('name', )
    list_editable = ('is_active', )
