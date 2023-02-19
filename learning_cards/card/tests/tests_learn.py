from datetime import datetime
from pprint import pprint
from unittest import mock

from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse

from card.models import Card, Statistic

from freezegun import freeze_time

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

    def test_get_learning_cards(self):
        cards_for_learning = list(self.user.profile.get_learning_cards('python'))
        box = self.user.box_set.filter(slug='python').first()
        equal_cards = []
        [equal_cards.extend(category.card_set.all()) for category in box.category.all()]
        self.assertEqual(len(cards_for_learning), 5)
        self.assertListEqual(cards_for_learning, equal_cards[:5])

    def test_can_view_learning_page(self):
        response = self.client.get(reverse('learning', args=['python']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learn/learning.html')

    def test_learning_view_changing_cards(self):
        self.client.post(reverse('learn'), {'day_limit': 3})

        response_1 = self.client.get(reverse('learning', args=['python']))
        learning_list_cards = response_1.context['cards']
        self.assertEqual(len(learning_list_cards), 3)
        self.assertIn(response_1.context["learning_card"], learning_list_cards)

        response_2 = self.client.post(reverse('learning', args=['python']), {'learned': response_1.context["learning_card"].id,
                                                                             'learning_card': response_1.context["learning_card"].id,
                                                                             'id': [card.id for card in response_1.context["cards"]]})
        self.assertEqual(len(response_2.context['cards']), 2)
        self.assertIn(response_2.context["learning_card"], response_2.context["cards"])

        response_3 = self.client.post(reverse('learning', args=['python']),
                                    {'learned': response_2.context["learning_card"].id,
                                     'learning_card': response_2.context["learning_card"].id,
                                     'id': [card.id for card in response_2.context["cards"]]})
        self.assertEqual(len(response_3.context['cards']), 1)
        self.assertIn(response_3.context["learning_card"], response_3.context["cards"])

        response_4 = self.client.post(reverse('learning', args=['python']),
                                      {'learned': response_3.context["learning_card"].id,
                                       'learning_card': response_3.context["learning_card"].id,
                                       'id': [card.id for card in response_3.context["cards"]]})
        self.assertEqual(response_4.status_code, 302)
        self.assertURLEqual(response_4.url, reverse('congratulations'))

class StatisticsTestCase(TestCase):
    fixtures = ['user.json', 'profile.json', 'category.json', 'card.json', 'box.json']

    def setUp(self):
        self.user_login_data = {
            'username': 'allex',
            'password': 'rootroot'
        }

        self.client.login(**self.user_login_data)
        self.user = get_user(self.client)
        return super().setUp()


    def test_statistic(self):
        self.client.post(reverse('learn'), {'day_limit': 5})
        cards = Card.objects.filter(author=self.user, )[:5]
        for card in cards:
            Statistic.objects.create(user_id=self.user, card_id=card)
        statistic = Statistic.objects.filter(user_id=self.user)
        self.assertEqual(len(statistic), 5)

    def test_get_statistic(self):
        cards = Card.objects.filter(author=self.user)[:10]

        date_1 = datetime(2010, 1, 1, hour=12, minute=1)
        for card in cards[:5]:
            self.make_show(card, date_1)

        date_2 = datetime(2010, 1, 2, hour=12, minute=1)
        for card in cards[5:10]:
            self.make_show(card, date_2)
        for card in cards[:10]:
            self.make_show(card, date_2)
            self.make_statistic(card, date_2)

        date_3 = datetime(2010, 1, 3, hour=12, minute=1)
        for card in cards[0:10]:
            self.make_show(card, date_3)
            self.make_statistic(card, date_3)

        with freeze_time(datetime(2010, 1, 4, hour=15, minute=1)):
            statistic = self.user.profile.get_statistic(period=5)
        self.assertEqual(statistic, [{"x": "2009-12-31", "learned": 0, "repeat": 0},
                                     {"x": "2010-01-01", "learned": 5, "repeat": 0},
                                     {"x": "2010-01-02", "learned": 5, "repeat": 10},
                                     {"x": "2010-01-03", "learned": 0, "repeat": 10},
                                     {"x": "2010-01-04", "learned": 0, "repeat": 0}])

    def make_show(self, card, date):
        with freeze_time(date):
            card.add_count_shows()
            card.save()

    def make_statistic(self, card, date):
        with freeze_time(date):
            Statistic.objects.create(user_id=self.user, card_id=card)


