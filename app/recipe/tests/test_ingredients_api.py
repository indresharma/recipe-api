from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredients, Recipe
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredients-list')


class PublicIngredientAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@test.com',
                                                         'testpass')
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        Ingredients.objects.create(user=self.user, name='salt')
        Ingredients.objects.create(user=self.user, name='pepper')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        '''Test that ingredients for the authenticated user are returned'''
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'passpass'
        )
        Ingredients.objects.create(user=user2, name='chilli')
        ingredient = Ingredients.objects.create(user=self.user, name='salt')
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredients(self):
        payload = {'name': 'cheese'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredients.objects.filter(user=self.user,
                                            name=payload['name'])
        self.assertTrue(exists)

    def test_create_ingredients_invalid(self):
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        ingredient1 = Ingredients.objects.create(user=self.user, name='apple')
        ingredient2 = Ingredients.objects.create(user=self.user, name='salt')
        recipe = Recipe.objects.create(
            title='Apple Pie',
            time_minutes=30,
            price=40,
            user=self.user,
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        ingredient = Ingredients.objects.create(user=self.user, name='Lemon')
        Ingredients.objects.create(user=self.user, name='mint')
        recipe1 = Recipe.objects.create(
            title='Lemonade',
            time_minutes=5,
            price=5,
            user=self.user,
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Mojito',
            time_minutes=7,
            price=7,
            user=self.user,
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
