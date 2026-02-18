from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


class CustomUserAdmin(UserAdmin):
    """Административный интерфейс для управления пользователями."""
    model = User
    list_display = ["email", "username", "phone_number", "is_staff"]
    list_filter = ["is_staff", "is_active"]
    ordering = ["email"]
    search_fields = ["email", "username"]


admin.site.register(User, CustomUserAdmin)

