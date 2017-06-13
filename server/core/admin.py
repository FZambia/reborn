from django.contrib import admin
from core.models import Provider, Category, Source, Subscription, Entry
from django.db.models import Count


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):

    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ('name', 'user', 'is_active')
    search_fields = ('name', 'description',)
    list_editable = ('is_active', )


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):

    list_display = ('name', 'provider', 'num_subscriptions')
    search_fields = ('name', 'provider__name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(num_subscriptions=Count('subscription'))

    def num_subscriptions(self, obj):
      return obj.num_subscriptions

    num_subscriptions.short_description = 'subscription count'
    num_subscriptions.admin_order_field = 'num_subscriptions'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'source', 'score', )
    list_editable = ('source', 'score', )
    list_filter = ('user',)
    filter_horizontal = ('categories', )
    raw_id_fields = ('user', 'source', )


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):

    list_display = ('title', 'url', 'subscription', 'is_active', 'is_favorite')
    search_fields = ('title', 'url', 'content')
    list_editable = ('is_active', 'is_favorite')
