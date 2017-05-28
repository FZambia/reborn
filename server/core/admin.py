from django.contrib import admin
from core.models import Provider, Loader, Category, Subscription, Entry


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):

    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_editable = ('is_active', )


@admin.register(Loader)
class LoaderAdmin(admin.ModelAdmin):

    list_display = ('name', 'token', 'is_active')
    search_fields = ('name', )
    list_editable = ('is_active', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ('name', 'user', 'is_active')
    search_fields = ('name', 'description',)
    list_editable = ('is_active', )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'source', 'score', 'provider', )
    list_editable = ('source', 'score', )
    list_filter = ('user',)
    filter_horizontal = ('categories', )


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):

    list_display = ('title', 'url', 'subscription', 'is_active', 'is_favorite')
    search_fields = ('title', 'url', 'content')
    list_editable = ('is_active', 'is_favorite')
