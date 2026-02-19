from rest_framework import serializers

from locareward.models import Action, Location, Reward


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор локаций"""

    class Meta:
        model = Location
        fields = "__all__"
        read_only_fields = ["owner"]
        validators = [
            serializers.UniqueTogetherValidator(
                fields=["name"], queryset=Location.objects.all()
            )
        ]


class ActionSerializer(serializers.ModelSerializer):
    """Сериализатор действий"""

    class Meta:
        model = Action
        fields = "__all__"
        read_only_fields = ["owner"]
        validators = [
            serializers.UniqueTogetherValidator(
                fields=["name"], queryset=Action.objects.all()
            )
        ]


class RewardSerializer(serializers.ModelSerializer):
    """Сериализатор вознаграждений"""

    class Meta:
        model = Reward
        fields = "__all__"
        read_only_fields = ["owner"]
        validators = [
            serializers.UniqueTogetherValidator(
                fields=["name"], queryset=Reward.objects.all()
            )
        ]
