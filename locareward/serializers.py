from rest_framework import serializers

from locareward.models import Location, Action, Reward


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор локаций"""
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['owner']
        #validators


class ActionSerializer(serializers.ModelSerializer):
    """Сериализатор локаций"""
    class Meta:
        model = Action
        fields = '__all__'
        read_only_fields = ['owner']
        #validators


class RewardSerializer(serializers.ModelSerializer):
    """Сериализатор локаций"""
    class Meta:
        model = Reward
        fields = '__all__'
        read_only_fields = ['owner']
        #validators