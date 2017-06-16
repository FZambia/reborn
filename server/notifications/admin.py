from django.contrib import admin
from notifications.models import KeyValue, DashboardNotificationProfile


@admin.register(KeyValue)
class ProviderAdmin(admin.ModelAdmin):

    list_display = ('key', 'value')
    search_fields = ('key',)


@admin.register(DashboardNotificationProfile)
class DashboardNotificationAdmin(admin.ModelAdmin):

    list_display = ('dashboard', 'telegram_chat_id')
