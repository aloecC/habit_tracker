import datetime

from django.conf import settings
from django.db import models

from locareward.models import LikeAction, Location, NeedAction, Reward


class HabitBaseInfo(models.Model):
    """Абстрактная модель для Привычек"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Создатель привычки",
        related_name="%(class)s_habits",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Локация",
        related_name="%(class)s_habits",
    )

    class Meta:
        abstract = True


class HabitNice(HabitBaseInfo):
    """Модель приятной привычки"""

    like_action = models.ForeignKey(
        LikeAction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Любимое действие",
        related_name="%(class)s_habits",
    )

    is_pleasant = models.BooleanField(default=True, editable=False)

    def __str__(self):
        like_action_name = self.like_action.name if self.like_action else "Без действия"
        #  user_email = self.user.email if self.user else "Без пользователя"
        return f"Приятная: {like_action_name}"

    class Meta:
        verbose_name = "Приятная привычка"
        verbose_name_plural = "Приятные привычки"


class HabitUseful(HabitBaseInfo):
    """Модель полезной привычки"""

    PERIODICITY_CHOISE = [
        (1, "Каждый день"),
        (2, "Каждые два дня"),
        (3, "Каждые три дня"),
        (4, "Каждые четыре дня"),
        (5, "Каждые пять дней"),
        (6, "Каждые шесть дней"),
        (7, "Каждую неделю"),
    ]

    need_action = models.ForeignKey(
        NeedAction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Нужное действие",
        related_name="%(class)s_habits",
    )

    is_pleasant = models.BooleanField(default=False, editable=False)

    time_check = models.PositiveIntegerField(
        help_text="Время выполнения в секундах", default=120
    )

    created_at = models.DateField(auto_now_add=True)

    nice_habit = models.ForeignKey(
        HabitNice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="useful_habits",
    )

    time_of_day = models.TimeField(
        default=datetime.time(21, 30, 00), help_text="Время выполнения привычки"
    )

    reward = models.ForeignKey(Reward, on_delete=models.SET_NULL, null=True, blank=True)

    periodicity = models.IntegerField(
        default=1, choices=PERIODICITY_CHOISE, help_text="Раз во сколько дней"
    )

    is_public = models.BooleanField(default=False, editable=True)

    class Meta:
        verbose_name = "Полезная привычка"
        verbose_name_plural = "Полезные привычки"

    def __str__(self):
        need_action_name = self.need_action.name if self.need_action else "Без действия"
        #  user_email = self.user.email if self.user else "Без пользователя"
        return f"Полезная: {need_action_name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
