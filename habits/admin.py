from django.contrib import admin

from config import settings
from habits.models import HabitUseful, HabitNice


@admin.register(HabitUseful)
class HabitUseful(admin.ModelAdmin):
    """Административный интерфейс для управления полезными привычками."""
    list_display = (id, "user", "location", "action", "periodicity")
    list_filter = ("user", "location", "action")
    search_fields = (
        "user",
        "location",
        "action",
        "reward",
        "nice_habit"
    )


@admin.register(HabitNice)
class HabitNice(admin.ModelAdmin):
    """Административный интерфейс для управления приятными привычками."""
    list_display = (id, "user", "location", "action")
    list_filter = ("user", "location", "action")
    search_fields = (
        "user",
        "location",
        "action"
    )