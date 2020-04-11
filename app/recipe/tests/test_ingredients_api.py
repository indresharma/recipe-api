from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredients
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
