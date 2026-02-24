from rest_framework import serializers

from habits.models import HabitNice, HabitUseful
from habits.validators import RewardOrNiceHabitValidator


class HabitNiceSerializer(serializers.ModelSerializer):
    """Сериализатор приятных привычек"""

    location_name = serializers.CharField(source="location.name", read_only=True)
    like_action_name = serializers.CharField(source="like_action.name", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = HabitNice
        fields = "__all__"
        read_only_fields = ["user", "is_pleasant", "location_name", "like_action_name"]


class HabitUsefulSerializer(serializers.ModelSerializer):
    """Сериализатор полезных привычек"""

    location_name = serializers.CharField(source="location.name", read_only=True)
    need_action_name = serializers.CharField(source="need_action.name", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    nice_habit_name = serializers.CharField(
        source="nice_habit.like_action.name", read_only=True
    )
    reward_name = serializers.CharField(source="reward.name", read_only=True)

    class Meta:
        model = HabitUseful
        fields = "__all__"
        read_only_fields = [
            "user",
            "is_pleasant",
            "location_name",
            "need_action_name",
            "nice_habit_name",
            "reward_name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(
            RewardOrNiceHabitValidator(
                reward_field="reward", associated_habit_field="nice_habit"
            )
        )

    def validate(self, data):
        time_to_complete = data.get("time_сheck")
        if time_to_complete is not None and time_to_complete >= 120:
            raise serializers.ValidationError(
                "Время выполнения не может быть больше 120 секунд (2 минуты)."
            )

        return data
