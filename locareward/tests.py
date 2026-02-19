from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from locareward.models import Location, Action, Reward
from users.models import User


class LocationTest(APITestCase):
    """Тесты проверки локаций"""
    def setUp(self):
        # Создаем группы
        self.moderator_group = Group.objects.create(name='Модераторы')

        # Создаем пользователей и добавляем их в группы
        self.user = User.objects.create_user(username='user', email='user@mail.ru', password='password')
        self.moderator = User.objects.create_user(username='moderator', email='moderator@mail.ru', password='password')
        self.moderator_group.user_set.add(self.moderator)

        # Создаем курс и урок для тестирования
        self.location = Location.objects.create(name='Дом', description='Test Description', owner=self.user)

    def test_create_location(self):
        """Тест создания локации"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Test',
            'description': 'Test'
        }
        response = self.client.post(
            '/locareward/locations/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_update_location(self):
        """Тест обновления локации"""
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'U Test',
        }
        response = self.client.patch(
            f'/locareward/locations/{self.location.id}/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_list_location(self):
        """Тест вывода списка локаций"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/locareward/locations/',
        )

        self.assertEqual(
         response.status_code,
         status.HTTP_200_OK
     )

        self.assertIsInstance(response.json(), dict)

        self.assertIn('results', response.json())
        self.assertIsInstance(response.json()['results'], list)

        results = response.json()['results']
        self.assertGreater(len(results), 0)  # Проверяем, что список не пуст
        self.assertEqual(results[0]['name'], 'Дом')  # Проверяем название

    def test_retrieve_location(self):
        """Тест просмотра локации"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/locareward/locations/{self.location.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_delete_location(self):
        """Тест удаления локации"""
        self.client.force_authenticate(user=self.user)

        self.assertIsNotNone(Location.objects.filter(id=self.location.id).first())

        response = self.client.delete(
            f'/locareward/locations/{self.location.id}/',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(Location.objects.filter(id=self.location.id).first())


class ActionTest(APITestCase):
    """Тесты проверки действия"""
    def setUp(self):
        # Создаем группы
        self.moderator_group = Group.objects.create(name='Модераторы')

        # Создаем пользователей и добавляем их в группы
        self.user = User.objects.create_user(username='user', email='user@mail.ru', password='password')
        self.moderator = User.objects.create_user(username='moderator', email='moderator@mail.ru', password='password')
        self.moderator_group.user_set.add(self.moderator)

        # Создаем курс и урок для тестирования
        self.action = Action.objects.create(name='Бегать по утрам', description='Test Description', owner=self.user)

    def test_create_action(self):
        """Тест создания действия"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Test',
            'description': 'Test'
        }
        response = self.client.post(
            '/locareward/actions/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_update_action(self):
        """Тест обновления действия"""
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'U Test',
        }
        response = self.client.patch(
            f'/locareward/actions/{self.action.id}/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_list_action(self):
        """Тест вывода списка действия"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/locareward/actions/',
        )

        self.assertEqual(
         response.status_code,
         status.HTTP_200_OK
     )

        self.assertIsInstance(response.json(), dict)

        self.assertIn('results', response.json())
        self.assertIsInstance(response.json()['results'], list)

        results = response.json()['results']
        self.assertGreater(len(results), 0)  # Проверяем, что список не пуст
        self.assertEqual(results[0]['name'], 'Бегать по утрам')  # Проверяем название

    def test_retrieve_action(self):
        """Тест просмотра действия"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/locareward/actions/{self.action.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_delete_action(self):
        """Тест удаления действия"""
        self.client.force_authenticate(user=self.user)

        self.assertIsNotNone(Action.objects.filter(id=self.action.id).first())

        response = self.client.delete(
            f'/locareward/actions/{self.action.id}/',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(Action.objects.filter(id=self.action.id).first())


class RewardTest(APITestCase):
    """Тесты проверки вознаграждения"""
    def setUp(self):
        # Создаем группы
        self.moderator_group = Group.objects.create(name='Модераторы')

        # Создаем пользователей и добавляем их в группы
        self.user = User.objects.create_user(username='user', email='user@mail.ru', password='password')
        self.moderator = User.objects.create_user(username='moderator', email='moderator@mail.ru', password='password')
        self.moderator_group.user_set.add(self.moderator)

        # Создаем курс и урок для тестирования
        self.reward = Reward.objects.create(name='Шоколад', description='Test Description', owner=self.user)

    def test_create_reward(self):
        """Тест создания вознаграждения"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Test',
            'description': 'Test'
        }
        response = self.client.post(
            '/locareward/rewards/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_update_reward(self):
        """Тест обновления вознаграждения"""
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'U Test',
        }
        response = self.client.patch(
            f'/locareward/rewards/{self.reward.id}/',
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_list_reward(self):
        """Тест вывода списка вознаграждений"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/locareward/rewards/',
        )

        self.assertEqual(
         response.status_code,
         status.HTTP_200_OK
     )

        self.assertIsInstance(response.json(), dict)

        self.assertIn('results', response.json())
        self.assertIsInstance(response.json()['results'], list)

        results = response.json()['results']
        self.assertGreater(len(results), 0)  # Проверяем, что список не пуст
        self.assertEqual(results[0]['name'], 'Шоколад')  # Проверяем название

    def test_retrieve_reward(self):
        """Тест просмотра вознаграждения"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/locareward/rewards/{self.reward.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_delete_reward(self):
        """Тест удаления вознаграждения"""
        self.client.force_authenticate(user=self.user)

        self.assertIsNotNone(Reward.objects.filter(id=self.reward.id).first())

        response = self.client.delete(
            f'/locareward/rewards/{self.reward.id}/',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(Reward.objects.filter(id=self.reward.id).first())