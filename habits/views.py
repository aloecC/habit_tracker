from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from habits.models import HabitNice, HabitUseful
from habits.paginators import HabitsPagination
from habits.permisions import IsModerator, IsOwner
from habits.serializers import HabitNiceSerializer, HabitUsefulSerializer
from locareward.models import Location, Reward, Action
from users.models import User


class HabitUsefulCreateAPIView(generics.CreateAPIView):
    """Создание полезной привычки"""
    serializer_class = HabitUsefulSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        action_id = self.request.data.get('action')

        if self.request.data.get('reward'):
            reward_id = self.request.data.get('reward')
            try:
                reward = Reward.objects.get(id=reward_id)
                if reward.owner and reward.owner != self.request.user:
                    raise PermissionDenied("Вы не можете добавлять чужие вознагрждения")
            except Reward.DoesNotExist:
                raise PermissionDenied("Вознаграждение не найдено")

        location_id = self.request.data.get('location')

        if self.request.data.get('nice_habit'):
            nice_habit_id = self.request.data.get('nice_habit')
            try:
                nice_habit = HabitNice.objects.get(id=nice_habit_id)
                if nice_habit.user and nice_habit.user != self.request.user:
                    raise PermissionDenied("Вы не можете добавлять чужие приятные привычки")
            except HabitNice.DoesNotExist:
                raise PermissionDenied("Приятная привычка не найдена")

        try:
            action = Action.objects.get(id=action_id)

            if action.owner and action.owner != self.request.user:
                raise PermissionDenied("Вы не можете добавлять чужие действия")

        except Action.DoesNotExist:
            raise PermissionDenied("Действие не найдено")

        try:
            location = Location.objects.get(id=location_id)
            if location.owner and location.owner != self.request.user:
                raise PermissionDenied("Вы не можете добавлять чужие локации")

        except Location.DoesNotExist:
            raise PermissionDenied("Локация не найдена")

        habituseful = serializer.save(user=self.request.user)


class HabitUsefulRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр полезной привычки"""
    permission_classes = [IsAuthenticated]
    serializer_class = HabitNiceSerializer
    queryset = HabitUseful.objects.all()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.groups.filter(name='Модераторы').exists() or obj.user == self.request.user:
            return obj
        raise PermissionDenied("У вас нет доступа к этому объекту.")


class HabitUsefulUpdateAPIView(generics.UpdateAPIView):
    """Обновление полезной привычки"""

    serializer_class = HabitUsefulSerializer
    permission_classes = [IsAuthenticated]
    queryset = HabitUseful.objects.all()

    def get_object(self):
        obj = super().get_object()
        if obj.user == self.request.user:
            return obj
        raise PermissionDenied("У вас нет доступа к этому объекту.")


class HabitUsefulDestroyAPIView(generics.DestroyAPIView):
    """Удаление полезной привычки"""

    serializer_class = HabitUsefulSerializer
    permission_classes = [IsAuthenticated]
    queryset = HabitUseful.objects.all()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.groups.filter(name='Модераторы').exists() or obj.user == self.request.user:
            return obj
        raise PermissionDenied("У вас нет доступа к этому объекту.")


class HabitUsefulListAPIView(generics.ListAPIView):
    """Просмотр списка своих полезных привычек"""
    permission_classes = [IsAuthenticated]
    serializer_class = HabitUsefulSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name="Модераторы").exists():
                return HabitUseful.objects.all()
            else:
                return HabitUseful.objects.filter(user=self.request.user)


class HabitUsefulPublicListAPIView(generics.ListAPIView):
    """Просмотр списка публичных полезных привычек"""
    permission_classes = [IsAuthenticated]
    serializer_class = HabitUsefulSerializer

    def get_queryset(self):
        return HabitUseful.objects.filter(is_public=True)


class HabitNiceCreateAPIView(generics.CreateAPIView):
    """Создание приятной привычки"""
    permission_classes = [IsAuthenticated]
    serializer_class = HabitNiceSerializer

    def perform_create(self, serializer):
        action_id = self.request.data.get('action')
        location_id = self.request.data.get('location')
        try:
            action = Action.objects.get(id=action_id)

            if action.owner and action.owner != self.request.user:
                raise PermissionDenied("Вы не можете добавлять чужие действия")

        except Action.DoesNotExist:
            raise PermissionDenied("Действие не найдено")

        try:
            location = Location.objects.get(id=location_id)
            if location.owner and location.owner != self.request.user:
                raise PermissionDenied("Вы не можете добавлять чужие локации")

        except Location.DoesNotExist:
            raise PermissionDenied("Локация не найдена")

        habitnice = serializer.save(user=self.request.user)


class HabitNiceRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр приятной привычки"""
    permission_classes = [IsAuthenticated]
    serializer_class = HabitNiceSerializer
    queryset = HabitNice.objects.all()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.groups.filter(name='Модераторы').exists() or obj.user == self.request.user:
            return obj
        raise PermissionDenied("У вас нет доступа к этому объекту.")


class HabitNiceUpdateAPIView(generics.UpdateAPIView):
    """Обновление приятной привычки"""
    permission_classes = [IsAuthenticated]
    serializer_class = HabitNiceSerializer
    queryset = HabitNice.objects.all()

    def get_object(self):
        obj = super().get_object()
        if obj.user == self.request.user:
            return obj
        raise PermissionDenied("У вас нет доступа к этому объекту.")


class HabitNiceDestroyAPIView(generics.DestroyAPIView):
    """Удаление приятной привычки"""
    permission_classes = [IsAuthenticated]
    queryset = HabitNice.objects.all()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.groups.filter(name='Модераторы').exists() or obj.user == self.request.user:
            return obj
        raise PermissionDenied("У вас нет доступа к этому объекту.")


class HabitNiceListAPIView(generics.ListAPIView):
    """Просмотр списка приятных привычек"""
    serializer_class = HabitNiceSerializer
    pagination_class = HabitsPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name="Модераторы").exists():
                return HabitNice.objects.all()
            else:
                return HabitNice.objects.filter(user=self.request.user)


class HabitUsefulUserListAPIView(generics.ListAPIView):
    """Просмотр списка полезных привычек определенного пользователя"""

    serializer_class = HabitUsefulSerializer
    permission_classes = [IsModerator]
    pagination_class = HabitsPagination

    def get_queryset(self):
        user_id = self.kwargs.get("pk")
        user = User.objects.get(pk=user_id)
        return HabitUseful.objects.filter(user=user)
