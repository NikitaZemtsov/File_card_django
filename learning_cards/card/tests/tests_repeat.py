import json
from datetime import datetime

from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse

from card.models import Card, Statistic

from freezegun import freeze_time


class RepeatViewTestCase(TestCase):
    fixtures = ['user.json', 'profile.json', 'category.json', 'card_with_statistic.json', 'box.json', 'statistic.json']

    def setUp(self):
        self.user_login_data = {
            'username': 'allex',
            'password': 'rootroot'
        }

        self.client.login(**self.user_login_data)
        self.user = get_user(self.client)
        return super().setUp()

    def test_get_cards_to_repeat(self):
        with freeze_time(datetime(2023, 2, 18, hour=15, minute=1)):
            cards_for_repeat = list(self.user.profile.get_cards_to_repeat)
        cards_comparison = list(Card.objects.filter(pk__in=[24, 25, 26, 27, 28]))
        self.assertEqual(len(cards_for_repeat), 5)
        self.assertListEqual(cards_for_repeat, cards_comparison)

    def test_can_view_repeat_page(self):
        response = self.client.get(reverse('repeat'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learn/learning.html')

    @freeze_time(datetime(2023, 2, 18, hour=15, minute=1))
    def test_repeat_view_changing_cards(self):
        response_1 = self.client.get(reverse('repeat'))
        repeat_list_cards = response_1.context['cards']
        self.assertEqual(len(repeat_list_cards), 5)
        self.assertIn(response_1.context["learning_card"], repeat_list_cards)

        response_2 = self.client.post(reverse('repeat'), {'learned': response_1.context["learning_card"].id,
                                                          'learning_card': response_1.context["learning_card"].id,
                                                          'id': [card.id for card in response_1.context["cards"]]})
        self.assertEqual(len(response_2.context['cards']), 4)
        self.assertIn(response_2.context["learning_card"], response_2.context["cards"])

        response_3 = self.client.post(reverse('repeat'),
                                      {'learned': response_2.context["learning_card"].id,
                                       'learning_card': response_2.context["learning_card"].id,
                                       'id': [card.id for card in response_2.context["cards"]]})
        self.assertEqual(len(response_3.context['cards']), 3)
        self.assertIn(response_3.context["learning_card"], response_3.context["cards"])

        response_4 = self.client.post(reverse('repeat'),
                                      {'learned': response_3.context["learning_card"].id,
                                       'learning_card': response_3.context["learning_card"].id,
                                       'id': [card.id for card in response_3.context["cards"]]})
        self.assertEqual(len(response_4.context['cards']), 2)
        self.assertIn(response_4.context["learning_card"], response_4.context["cards"])

        response_5 = self.client.post(reverse('repeat'),
                                      {'learned': response_4.context["learning_card"].id,
                                       'learning_card': response_4.context["learning_card"].id,
                                       'id': [card.id for card in response_4.context["cards"]]})
        self.assertEqual(len(response_5.context['cards']), 1)
        self.assertIn(response_5.context["learning_card"], response_5.context["cards"])

        response_6 = self.client.post(reverse('repeat'),
                                      {'learned': response_5.context["learning_card"].id,
                                       'learning_card': response_5.context["learning_card"].id,
                                       'id': [card.id for card in response_5.context["cards"]]})
        self.assertEqual(response_6.status_code, 302)
        self.assertURLEqual(response_6.url, reverse('learn'))

        statistics = Statistic.objects.filter(date=datetime(2023, 2, 18, hour=15, minute=1))
        cards_pk_statistic = [row.card_id.pk for row in statistics]
        self.assertListEqual(sorted(cards_pk_statistic), [24, 25, 26, 27, 28])

    @freeze_time(datetime(2023, 2, 18, hour=14, minute=1))
    def test_chart(self):
        response_1 = self.client.get(reverse('learn'))
        self.assertEqual(json.loads(response_1.context['statistics']), [{"x": "2023-02-12", "learned": 0, "repeat": 0},
                                                                        {"x": "2023-02-13", "learned": 0, "repeat": 0},
                                                                        {"x": "2023-02-14", "learned": 5, "repeat": 5},
                                                                        {"x": "2023-02-15", "learned": 5, "repeat": 10},
                                                                        {"x": "2023-02-16", "learned": 5, "repeat": 10},
                                                                        {"x": "2023-02-17", "learned": 0, "repeat": 15},
                                                                        {"x": "2023-02-18", "learned": 0, "repeat": 0}])
