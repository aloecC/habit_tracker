import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from locareward.models import Location, Action, Reward


class HabitBaseInfo(models.Model):
    """Абстрактная модель для Привычек"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Создатель привычки', default=1, related_name='%(class)s_habits')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Локация', related_name='%(class)s_habits')
    do_time = models.TimeField(
        default=datetime.time(11, 0, 0),
        help_text="Время выполнения привычки"
    )
    action = models.ForeignKey(Action, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Действие', related_name='%(class)s_habits')

    class Meta:
        abstract = True


class HabitNice(HabitBaseInfo):
    """Модель приятной привычки"""
    is_pleasant = models.BooleanField(default=True, editable=False)

    def __str__(self):
        return f"Приятная: {self.action.name} ({self.user.email})"

    class Meta:
        verbose_name = "Приятная привычка"
        verbose_name_plural = "Приятные привычки"


class HabitUseful(HabitBaseInfo):
    """Модель полезной привычки"""
    is_pleasant = models.BooleanField(default=False, editable=False)

    nice_habit = models.ForeignKey(
        HabitNice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="useful_habits"
    )

    reward = models.ForeignKey(
        Reward,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    periodicity = models.PositiveSmallIntegerField(default=1, help_text="Раз во сколько дней")

    class Meta:
        verbose_name = "Полезная привычка"
        verbose_name_plural = 'Полезные привычки'
