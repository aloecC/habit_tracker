from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import HabitNice, HabitUseful
from locareward.models import Location, Action, Reward
from users.models import User


class HabitNiceTest(APITestCase):
    """Тесты проверки приятной привычки"""
    def setUp(self):
        self.moderator_group = Group.objects.create(name='Модераторы')

        self.user = User.objects.create_user(username='user', email='user@mail.ru', password='password')
        self.moderator = User.objects.create_user(username='moderator', email='moderator@mail.ru', password='password')
        self.moderator_group.user_set.add(self.moderator)

        self.location = Location.objects.create(name='Дом', description='Test Description', owner=self.user)
        self.action = Action.objects.create(name='Бегать по утрам', description='Test Description', owner=self.user)
        self.action_2 = Action.objects.create(name='Бегать по утрам', description='Test Description', owner=self.user)

        self.habit_nice = HabitNice.objects.create(action=self.action, location=self.location, user=self.user)

    def test_create_habit_nice(self):
        """Тест создания приятной привычки"""
        self.client.force_authenticate(user=self.user)
        data = {
            'action': f"{self.action.id}",
            'location': f'{self.location.id}'
        }
        response = self.client.post(
            '/habits/habitnice/create/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_update_habit_nice(self):
        """Тест обновления приятной привычки"""
        self.client.force_authenticate(user=self.user)

        data = {
            'action': f'{self.action_2.id}',
            'location': f'{self.location.id}',
        }
        response = self.client.patch(
            f'/habits/habitnice/update/{self.habit_nice.id}/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_list_habit_nice(self):
        """Тест вывода списка приятных привычек"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/habits/habitnices/',
        )

        self.assertEqual(
         response.status_code,
         status.HTTP_200_OK
     )

        self.assertIsInstance(response.json(), dict)

        self.assertIn('results', response.json())
        self.assertIsInstance(response.json()['results'], list)

        results = response.json()['results']
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['location'], self.location.id)

    def test_retrieve_habit_nice(self):
        """Тест просмотра приятной привычки"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/habits/habitnice/{self.habit_nice.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_delete_habit_nice(self):
        """Тест удаления приятной привычки"""
        self.client.force_authenticate(user=self.user)

        self.assertIsNotNone(HabitNice.objects.filter(id=self.habit_nice.id).first())

        response = self.client.delete(
            f'/habits/habitnice/delete/{self.habit_nice.id}/',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(HabitNice.objects.filter(id=self.habit_nice.id).first())


class HabitUsefulTest(APITestCase):
    """Тесты проверки полезной привычки"""
    def setUp(self):
        self.moderator_group = Group.objects.create(name='Модераторы')

        self.user = User.objects.create_user(username='user', email='user@mail.ru', password='password')
        self.moderator = User.objects.create_user(username='moderator', email='moderator@mail.ru', password='password')
        self.moderator_group.user_set.add(self.moderator)

        self.location = Location.objects.create(name='Дом', description='Test Description', owner=self.user)
        self.action = Action.objects.create(name='Холодный душ', description='Test Description', owner=self.user)
        self.action_2 = Action.objects.create(name='Бегать по утрам', description='Test Description', owner=self.user)
        self.reward = Reward.objects.create(name='Шоколад', description='Test Description', owner=self.user)

        self.habit_userful = HabitUseful.objects.create(action=self.action, location=self.location, reward=self.reward, user=self.user)
        self.habit_userful_2 = HabitUseful.objects.create(action=self.action_2, location=self.location, reward=self.reward,
                                                        user=self.user, is_public=True)
        self.habit_nice = HabitNice.objects.create(action=self.action, location=self.location, user=self.user)

    def test_create_habit_userful(self):
        """Тест создания полезной привычки"""
        self.client.force_authenticate(user=self.user)
        data = {
            'action': f"{self.action.id}",
            'location': f'{self.location.id}',
            'reward': f'{self.reward.id}'
        }
        response = self.client.post(
            '/habits/habituseful/create/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_update_habit_userful(self):
        """Тест обновления полезной привычки"""
        self.client.force_authenticate(user=self.user)

        data = {
            'action': f'{self.action_2.id}',
            'location': f'{self.location.id}',
            'reward': f'{self.reward.id}'
        }
        response = self.client.patch(
            f'/habits/habituseful/update/{self.habit_userful.id}/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_list_habit_userful(self):
        """Тест вывода списка своих полезных привычек"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/habits/habitusefuls/',
        )

        self.assertEqual(
         response.status_code,
         status.HTTP_200_OK
     )

        self.assertIsInstance(response.json(), dict)

        self.assertIn('results', response.json())
        self.assertIsInstance(response.json()['results'], list)

        results = response.json()['results']
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['location'], self.location.id)

    def test_list_public_habit_userful(self):
        """Тест вывода списка публичгных полезных привычек"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/habits/habitusefuls/public/',
        )

        self.assertEqual(
         response.status_code,
         status.HTTP_200_OK
     )

        self.assertIsInstance(response.json(), dict)

        self.assertIn('results', response.json())
        self.assertIsInstance(response.json()['results'], list)

        results = response.json()['results']
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['action'], self.action_2.id)

    def test_retrieve_habit_userful(self):
        """Тест просмотра полезной привычки"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/habits/habituseful/{self.habit_userful.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_delete_habit_userful(self):
        """Тест удаления полезной привычки"""
        self.client.force_authenticate(user=self.user)

        self.assertIsNotNone(HabitUseful.objects.filter(id=self.habit_userful.id).first())

        response = self.client.delete(
            f'/habits/habituseful/delete/{self.habit_userful.id}/',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(HabitUseful.objects.filter(id=self.habit_userful.id).first())

    def test_habit_useful_user_list(self):
        """Тест просмотра списка полезных привычек определенного пользователя"""
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(
            f'/habits/moderator/{self.user.id}/habitusefuls/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIsInstance(response.json(), dict)

        self.assertIn('results', response.json())
        self.assertIsInstance(response.json()['results'], list)

        results = response.json()['results']
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['user'], self.user.id)

