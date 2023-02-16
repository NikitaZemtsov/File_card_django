from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse

from card.models import Card


class LearnViewTestCase(TestCase):
    fixtures = ['user.json', 'profile.json', 'category.json', 'card.json', 'box.json']

    def setUp(self):
        self.user_login_data = {
            'username': 'allex',
            'password': 'rootroot'
        }

        self.client.login(**self.user_login_data)
        self.user = get_user(self.client)
        return super().setUp()

    def test_can_view_learn_page(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learn/learn.html')

    def test_box_list(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['boxes']), 2)
        self.assertEqual(response.context['boxes'][0].pk, 14)
        self.assertEqual(response.context['boxes'][1].pk, 15)

    def test_form_day_limit(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['day_limit'].value(), 5)

    def test_learned_today_zero(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['learned'], 0)

    def test_add_count_shows(self):
        cards = list(self.user.card_set.all()[:5])
        [card.add_count_shows() for card in cards]
        [card.save() for card in cards]
        cards_learned = list(Card.objects.filter(author=self.user, count_shows=1))
        self.assertListEqual(cards_learned, cards)

    def test_learned_today_not_zero(self):
        cards = self.user.card_set.all()[:5]
        [card.add_count_shows() for card in cards]
        [card.save() for card in cards]
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['learned'], 5)

    def test_need_repeat_today_zero(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['repeat'], 0)