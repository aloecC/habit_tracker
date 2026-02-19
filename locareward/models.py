from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class BaseInfo(models.Model):
    """Абстрактная модель для Локаций, Действий и Наград"""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1, related_name="+"
    )

    class Meta:
        abstract = True


class Location(BaseInfo):
    """Модель Локаций"""

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return self.name


class Action(BaseInfo):
    """Модель Действий"""

    class Meta:
        verbose_name = "Действие"
        verbose_name_plural = "Действия"

    def __str__(self):
        return self.name


class Reward(BaseInfo):
    """Модель Наград"""

    class Meta:
        verbose_name = "Вознаграждение"
        verbose_name_plural = "Вознаграждения"

    def __str__(self):
        return self.name
