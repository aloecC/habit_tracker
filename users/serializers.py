from rest_framework import serializers

from habits.serializers import HabitUsefulSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя"""

    habituseful_habits = HabitUsefulSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"


class UserSerializerForAnother(serializers.ModelSerializer):
    """Сериализатор модели пользователя для посторонних"""

    habituseful_habits = HabitUsefulSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "habituseful_habits"]


class UserProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]  # Поля для редактирования
        extra_kwargs = {"password": {"write_only": True}}  # Пароль только для записи


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(
            validated_data["password"]
        )  # Храните пароль в зашифрованном виде
        user.save()
        return user
