from rest_framework import serializers
from core.models import Category, Provider, Subscription, Entry


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'description')

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super(CategorySerializer, self).create(validated_data)


class ProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Provider
        fields = ('id', 'name')


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('id', 'provider', 'source', 'score', 'categories',)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super(SubscriptionSerializer, self).create(validated_data)


class EntrySerializer(serializers.ModelSerializer):

    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = Entry
        fields = '__all__'
