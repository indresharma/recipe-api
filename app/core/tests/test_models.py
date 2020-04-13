from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def sample_user(email='test@test.com', password='testpass'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = 'testuser1@test.com'
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = 'testuser1@TEST.COM'
        user = get_user_model().objects.create_user(
            email=email,
            password='testpassword'
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpassword')

    def test_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'testsuperuser@gmail.com',
            'testpassword'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_model(self):
        '''Test to create a tag and verify it converts to the correct str
        representation'''
        tag = models.Tag.objects.create(user=sample_user(), name='Vegan')
        self.assertEqual(str(tag), tag.name)

    def test_ingredients_model(self):
        ingredient = models.Ingredients.objects.create(user=sample_user(),
                                                       name='oregano')
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='biryani',
            time_minutes=30,
            price=50,
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        '''Test that image is saved in the correct location'''
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')
        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
