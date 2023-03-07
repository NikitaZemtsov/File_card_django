import pprint

from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse

from ..models import Category
from ..utils import encrypt, decrypt


class ShareViewTestCase(TestCase):
    fixtures = ['user.json', 'profile.json', 'category.json', 'card.json', 'box.json']

    def setUp(self):
        self.user_login_data = {
            'username': 'allex',
            'password': 'rootroot'
        }

        self.client.login(**self.user_login_data)
        self.user = get_user(self.client)
        return super().setUp()

    def test_can_view_share_categories(self):
        response = self.client.get(reverse('share_categories'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'share/share_categories.html')

    def test_view_form_share_categories(self):
        self.categories_obj = self.user.category_set.all()
        response = self.client.get(reverse('share_categories'))

        self.assertEqual(response.status_code, 200)

        form_categories = response.context['form']['category']

        self.assertEqual(len(form_categories), 2)
        self.assertEqual(form_categories[0].data.get('value').value, self.categories_obj[0].pk)
        self.assertEqual(form_categories[1].data.get('value').value, self.categories_obj[1].pk)

    def test_make_share_link(self):
        data_category = {'category': [4, 5]}
        response = self.client.post(reverse('share_categories'), data_category)

        category = decrypt(response.context['link'].split('/')[-1])

        self.assertEqual(category, '4,5')

    def test_make_share_link(self):
        data_category = {'category': [4, 5]}
        response = self.client.post(reverse('share_categories'), data_category)

        category = decrypt(response.context['link'].split('/')[-1])

        self.assertEqual(category, '4,5')

    def test_shared_category(self):
        data_category = {'category': [4, 5]}
        response_1 = self.client.post(reverse('share_categories'), data_category)
        crypt_category_link = response_1.context['link'].split('/')[-1]

        response_2 = self.client.post(reverse('shared_categories', args=[crypt_category_link]))
        category = list(Category.objects.filter(pk__in=[4, 5]).all())
        self.assertEqual(list(response_2.context['categories']), category)

    def test_add_share_category(self):

        data_category = {'category': [4, 5]}
        response_1 = self.client.post(reverse('share_categories'), data_category)
        crypt_category_link = response_1.context['link'].split('/')[-1]

        user2_login_data = {
            'username': 'zema',
            'password': 'rootroot'
        }
        self.client.login(**user2_login_data)
        user2 = get_user(self.client)

        self.client.get(reverse('add_shared_category', args=[crypt_category_link]))
        category = [cat.pk for cat in Category.objects.filter(author=user2).all()]
        self.assertEqual(category, [2, 3, 6, 7])
