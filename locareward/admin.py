from django.contrib import admin

from config import settings
from locareward.models import NeedAction, LikeAction, Location, Reward


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Административный интерфейс для управления локациями."""

    list_display = ('id', "name", "description", "owner")
    list_filter = ("name", "description", "owner")
    search_fields = ("name", "description", "owner")
    raw_id_fields = ("owner",)


@admin.register(LikeAction)
class LikeActionAdmin(admin.ModelAdmin):
    """Административный интерфейс для управления любимыми действиями."""

    list_display = ('id', "name", "owner")
    list_filter = ("name", "owner")
    search_fields = ("name", "description", "owner")
    raw_id_fields = ("owner",)


@admin.register(NeedAction)
class NeedActionAdmin(admin.ModelAdmin):
    """Административный интерфейс для управления нужными действиями."""

    list_display = ('id', "name", "owner")
    list_filter = ("name", "owner")
    search_fields = ("name", "description", "owner")
    raw_id_fields = ("owner",)


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    """Административный интерфейс для управления вознаграждениями."""

    list_display = ('id', "name", "owner")
    list_filter = ("name", "owner")
    search_fields = ("name", "description", "owner")
    raw_id_fields = ("owner",)
