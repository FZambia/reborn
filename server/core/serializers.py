from rest_framework import serializers
from core.models import Category, Provider, Source, Subscription, Entry


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name')

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super(CategorySerializer, self).create(validated_data)


class ProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Provider
        fields = ('id', 'name')


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ('id', 'name', 'provider')


class SubscriptionSerializer(serializers.ModelSerializer):

    source = SourceSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'source', 'score', 'categories',)

    def save(self, **kwargs):
        provider = Provider.objects.get(pk=self.initial_data.get("provider"))
        source, _ = Source.objects.get_or_create(
            name=self.initial_data.get("source"),
            provider=provider
        )
        kwargs["source"] = source
        super().save(**kwargs)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super(SubscriptionSerializer, self).create(validated_data)


class EntrySerializer(serializers.ModelSerializer):

    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = Entry
        fields = '__all__'
