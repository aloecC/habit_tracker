from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny

from habits.models import HabitUseful, HabitNice
from habits.serializers import HabitUsefulSerializer, HabitNiceSerializer


class HabitUsefulCreateAPIView(generics.CreateAPIView):
    """Создание полезной привычки"""
    serializer_class = HabitUsefulSerializer


class HabitUsefulRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр полезной привычки"""
    serializer_class = HabitUsefulSerializer
    queryset = HabitUseful.objects.all()


class HabitUsefulUpdateAPIView(generics.UpdateAPIView):
    """Обновление полезной привычки"""
    serializer_class = HabitUsefulSerializer
    queryset = HabitUseful.objects.all()


class HabitUsefulDestroyAPIView(generics.DestroyAPIView):
    """Удаление полезной привычки"""
    serializer_class = HabitUsefulSerializer
    queryset = HabitUseful.objects.all()


class HabitUsefulListAPIView(generics.ListAPIView):
    """Просмотр списка своих полезных привычек"""
    serializer_class = HabitUsefulSerializer

    def get_queryset(self):
        return HabitUseful.objects.filter(owner=self.request.user)


class HabitUsefulPublicListAPIView(generics.ListAPIView):
    """Просмотр списка публичных полезных привычек"""
    serializer_class = HabitUsefulSerializer

    def get_queryset(self):
        return HabitUseful.objects.filter(is_public=True)


class HabitNiceCreateAPIView(generics.CreateAPIView):
    """Создание приятной привычки"""
    serializer_class = HabitNiceSerializer


class HabitNiceRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр приятной привычки"""
    serializer_class = HabitNiceSerializer
    queryset = HabitNice.objects.all()


class HabitNiceUpdateAPIView(generics.UpdateAPIView):
    """Обновление приятной привычки"""
    serializer_class = HabitNiceSerializer
    queryset = HabitNice.objects.all()


class HabitNiceDestroyAPIView(generics.DestroyAPIView):
    """Удаление приятной привычки"""
    queryset = HabitNice.objects.all()


class HabitNiceListAPIView(generics.ListAPIView):
    """Просмотр списка приятных привычек"""
    serializer_class = HabitNiceSerializer
    queryset = HabitNice.objects.all()