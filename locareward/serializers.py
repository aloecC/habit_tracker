from rest_framework import serializers

from locareward.models import Location, Reward, NeedAction, LikeAction


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


class NeedActionSerializer(serializers.ModelSerializer):
    """Сериализатор нужных действий"""

    class Meta:
        model = NeedAction
        fields = "__all__"
        read_only_fields = ["owner"]
        validators = [
            serializers.UniqueTogetherValidator(
                fields=["name"], queryset=NeedAction.objects.all()
            )
        ]


class LikeActionSerializer(serializers.ModelSerializer):
    """Сериализатор любимых действий"""

    class Meta:
        model = NeedAction
        fields = "__all__"
        read_only_fields = ["owner"]
        validators = [
            serializers.UniqueTogetherValidator(
                fields=["name"], queryset=LikeAction.objects.all()
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
