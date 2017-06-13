from django.contrib import admin
from notifications.models import KeyValue


@admin.register(KeyValue)
class ProviderAdmin(admin.ModelAdmin):

    list_display = ('key', 'value')
    search_fields = ('key',)
