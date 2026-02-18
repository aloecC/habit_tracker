from rest_framework import serializers

from habits.models import HabitNice, HabitUseful


class HabitNiceSerializer(serializers.ModelSerializer):
    """Сериализатор приятных привычек"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    action_name = serializers.CharField(source='action.name', read_only=True)

    class Meta:
        model = HabitNice
        fields = '__all__'
        #validators
        read_only_fields = ['user', 'is_pleasant', 'location_name', 'action_name']


class HabitUsefulSerializer(serializers.ModelSerializer):
    """Сериализатор полезных привычек"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    action_name = serializers.CharField(source='action.name', read_only=True)

    nice_habit_name = serializers.CharField(source='nice_habit.action.name', read_only=True)
    reward_name = serializers.CharField(source='reward.name', read_only=True)

    class Meta:
        model = HabitUseful
        fields = '__all__'
        #validators
        read_only_fields = [
            'user', 'is_pleasant', 'location_name', 'action_name',
            'nice_habit_name', 'reward_name'
        ]
