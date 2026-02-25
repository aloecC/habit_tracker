from django.contrib import admin

from habits.models import HabitNice, HabitUseful


@admin.register(HabitUseful)
class HabitUsefulAdmin(admin.ModelAdmin):
    """Административный интерфейс для управления полезными привычками."""

    list_display = ("id", "user", "location", "periodicity")
    list_filter = ("user", "location")
    search_fields = ("user", "location", "reward", "need_action")


@admin.register(HabitNice)
class HabitNiceAdmin(admin.ModelAdmin):
    """Административный интерфейс для управления приятными привычками."""

    list_display = ("id", "user", "location")
    list_filter = ("user", "location")
    search_fields = ("user", "location", "like_action")
