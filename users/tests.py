from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from locareward.models import Location, Action, Reward
from users.models import User


class UserTest(APITestCase):
    """Тесты проверки пользователя"""
    def setUp(self):
        self.moderator_group = Group.objects.create(name='Модераторы')

        self.user = User.objects.create_user(username='user', email='user@mail.ru', password='password')
        self.moderator = User.objects.create_user(username='moderator', email='moderator@mail.ru', password='password')
        self.moderator_group.user_set.add(self.moderator)

    def test_register_user(self):
        """Тест проверки регистрация пользователя"""
        data = {
            "username": "mowerator",
            "email": "mowerator@mail.ru",
            "password": "12345"
        }
        response = self.client.post(
            '/users/register/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


