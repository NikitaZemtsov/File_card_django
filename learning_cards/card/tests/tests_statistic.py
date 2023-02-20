from datetime import datetime

from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse

from card.models import Card, Statistic

from freezegun import freeze_time


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

    def test_get_statistic(self): # todo refactor func with fixture
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

