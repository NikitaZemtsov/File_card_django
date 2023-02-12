from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse
from pprint import pprint

from .models import User


# Create your tests here.
class BaseTest(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user = {
            'email': 'user@gmail.com',
            'username': 'user',
            'password1': 'rootroot',
            'password2': 'rootroot',
        }
        self.user_login = {
            'username': 'user',
            'password': 'rootroot'
        }

        self.user_unverified = {
            'username': 'user1',
            'password': 'rootroot'
        }
        self.user_short_password = {
            'email': 'user@gmail.com',
            'username': 'user',
            'password1': 'root',
            'password2': 'root',
        }
        self.user_unmatching_password = {

            'email': 'user@gmail.com',
            'username': 'user',
            'password1': 'testfault',
            'password2': 'test',
        }

        self.user_invalid_username = {
            'email': 'user@gmail.com',
            'username': 'userfault',
            'password1': 'rootroot',
            'password2': 'rootroot',
        }
        self.user_invalid_email = {
            'email': 'usergmail.com',
            'username': 'user',
            'password1': 'rootroot',
            'password2': 'rootroot',
        }
        return super().setUp()


class RegistretionTestCase(BaseTest):

    def test_can_view_page_correctly(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register/register.html')

    def test_can_register_user(self):
        response = self.client.post(self.register_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username=self.user.get('username'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertEqual(user.profile.day_limit, 5)

    def test_cant_register_user_withshortpassword(self):
        response = self.client.post(self.register_url, self.user_short_password, format='text/html')
        self.assertEqual(response.context[21].get('errors')[0], 'This password is too short. It must contain at least 8 characters.')

    def test_cant_register_user_with_unmatching_passwords(self):
        response = self.client.post(self.register_url, self.user_unmatching_password, format='text/html')
        self.assertEqual(response.context[-1].get('errors')[0], 'The two password fields didn’t match.')

    def test_cant_register_user_with_invalid_email(self):
        response = self.client.post(self.register_url, self.user_invalid_email, format='text/html')
        self.assertEqual(response.context[11].get('errors')[0], 'Enter a valid email address.')

    def test_cant_register_user_with_taken_email(self):
        self.client.post(self.register_url, self.user, format='text/html')
        response = self.client.post(self.register_url, self.user, format='text/html')
        self.assertEqual(response.context[6].get('errors')[0], 'A user with that username already exists.')


class LoginTestCase(BaseTest):

    def test_login_success(self):
        self.client.post(self.register_url, self.user, follow=True)
        response = self.client.login(**self.user_login)
        self.assertTrue(response)

    def test_cantlogin_with_unverified_user(self):
        self.client.post(self.register_url, self.user, follow=True)
        response = self.client.login(**self.user_unverified)
        self.assertFalse(get_user(self.client).is_authenticated)


class ProfileTestCase(BaseTest):
    pass

