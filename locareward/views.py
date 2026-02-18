from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from locareward.models import Location, Reward, Action
from locareward.serializers import LocationSerializer, RewardSerializer, ActionSerializer


class LocationViewSet(viewsets.ModelViewSet):
    """Виев-сет для локации"""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]


class ActionViewSet(viewsets.ModelViewSet):
    """Виев-сет для действия"""
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [AllowAny]


class RewardViewSet(viewsets.ModelViewSet):
    """Виев-сет для вознаграждения"""
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [AllowAny]
