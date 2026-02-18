from django.contrib import admin

from config import settings
from locareward.models import Location, Action, Reward


@admin.register(Location)
class Location(admin.ModelAdmin):
    """Административный интерфейс для управления локациями."""
    list_display = ('name', 'description', 'owner')
    list_filter = ('name', 'description', 'owner')
    search_fields = ('name', 'description', 'owner')
    raw_id_fields = ('owner',)


@admin.register(Action)
class Action(admin.ModelAdmin):
    """Административный интерфейс для управления действиями."""
    list_display = ('name', 'description', 'owner')
    list_filter = ('name', 'description', 'owner')
    search_fields = ('name', 'description', 'owner')
    raw_id_fields = ('owner',)


@admin.register(Reward)
class Reward(admin.ModelAdmin):
    """Административный интерфейс для управления вознаграждениями."""
    list_display = ('name', 'description', 'owner')
    list_filter = ('name', 'description', 'owner')
    search_fields = ('name', 'description', 'owner')
    raw_id_fields = ('owner',)


