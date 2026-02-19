from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from locareward.models import Action, Location, Reward
from locareward.paginators import LocarewardPagination
from locareward.permisions import IsOwner, IsModerator
from locareward.serializers import (ActionSerializer, LocationSerializer,
                                    RewardSerializer)


class LocationViewSet(viewsets.ModelViewSet):
    """Виев-сет для локации"""
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LocarewardPagination

    def get_queryset(self):
        if self.action == 'list':
            if self.request.user.is_authenticated:
                if self.request.user.groups.filter(name="Модераторы").exists():
                    return Location.objects.all()
                else:
                    return Location.objects.filter(owner=self.request.user)
            return Location.objects.none()  # Если не аутентифицирован
        return Location.objects.all()

    def list(self, request, *args, **kwargs):
        self.serializer_class = LocationSerializer
        return super().list(self, request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsOwner]
        elif self.action in ['retrieve', 'destroy']:
            self.permission_classes = [IsOwner | IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        location = serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ActionViewSet(viewsets.ModelViewSet):
    """Виев-сет для действия"""
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LocarewardPagination

    def get_queryset(self):

        if self.action == 'list':
            if self.request.user.is_authenticated:
                if self.request.user.groups.filter(name="Модераторы").exists():
                    return Action.objects.all()
                else:
                    return Action.objects.filter(owner=self.request.user)
            return Action.objects.none()
        return Action.objects.all()

    def list(self, request, *args, **kwargs):
        self.serializer_class = RewardSerializer
        return super().list(self, request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsOwner]
        elif self.action in ['retrieve', 'destroy']:
            self.permission_classes = [IsOwner | IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        action = serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class RewardViewSet(viewsets.ModelViewSet):
    """Виев-сет для вознаграждения"""
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LocarewardPagination

    def get_queryset(self):
        if self.action == 'list':
            if self.request.user.is_authenticated:
                if self.request.user.groups.filter(name="Модераторы").exists():
                    return Reward.objects.all()
                else:
                    return Reward.objects.filter(owner=self.request.user)
            return Reward.objects.none()
        return Reward.objects.all()

    def list(self, request, *args, **kwargs):
        self.serializer_class = RewardSerializer
        return super().list(self, request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsOwner]
        elif self.action in ['retrieve', 'destroy']:
            self.permission_classes = [IsOwner | IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        reward = serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
