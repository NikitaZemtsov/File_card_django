from datetime import datetime
from unittest import mock

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

    def test_form_day_limit_change(self):
        response = self.client.post(reverse('learn'), {'day_limit': 7})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['day_limit'].value(), '7')

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

    def test_add_count_shows_7_repeat(self):
        cards = list(self.user.card_set.all()[:5])
        [card.add_count_shows() for i in range(7) for card in cards]
        [card.save() for card in cards]
        cards_learned = list(Card.objects.filter(author=self.user, count_shows=-1))
        self.assertListEqual(cards_learned, cards)

    def test_learned_today_not_zero(self):
        cards = self.user.card_set.all()[:5]
        [card.add_count_shows() for card in cards]
        [card.save() for card in cards]
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['learned'], 5)

    @mock.patch('card.models.datetime')
    def test_learned_today_change_date(self, mocked_datetime):
        cards = self.user.card_set.all()[:5]
        [self.make_show(card) for card in cards]
        [card.save() for card in cards]
        mocked_datetime.now.return_value = datetime(2010, 1, 2, minute=1)
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['learned'], 0)

    def test_need_repeat_today_zero(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['repeat'], 0)

    @mock.patch('card.models.datetime')
    def test_need_repeat_today_not_zero(self, mocked_datetime):
        cards = self.user.card_set.all()[:5]
        cards = [self.make_show(card) for card in cards]
        mocked_datetime.now.return_value = datetime(2010, 1, 1, hour=15, minute=1)
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['repeat'], len(cards))

    @mock.patch('card.models.datetime')
    def make_show(self, card, mocked_datetime):
        mocked_datetime.now.return_value = datetime(2010, 1, 1, hour=12, minute=1)
        card.add_count_shows()
        card.save()


class LearningViewTestCase(TestCase):
    fixtures = ['user.json', 'profile.json', 'category.json', 'card.json', 'box.json']

    def setUp(self):
        self.user_login_data = {
            'username': 'allex',
            'password': 'rootroot'
        }

        self.client.login(**self.user_login_data)
        self.user = get_user(self.client)
        return super().setUp()

    def test_can_view_learning_page(self):
        response = self.client.get(reverse('learning', args=['python']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learn/learning.html')

    def test_get_learning_cards(self):
        cards_for_learning = list(self.user.profile.get_learning_cards('python'))
        box = self.user.box_set.filter(slug='python').first()
        equal_cards = []
        [equal_cards.extend(category.card_set.all()) for category in box.category.all()]
        self.assertEqual(len(cards_for_learning), 5)
        self.assertListEqual(cards_for_learning, equal_cards[:5])

