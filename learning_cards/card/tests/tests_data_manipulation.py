from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from pprint import pprint

from card.models import User, Category, Card, Box


class BaseTest(TestCase):
    fixtures = ['user.json']
    # -- Category data --
    data_category_oop = {'name': 'OOP',
                         'slug': 'oop',
                         'description': 'oop'
                         }
    data_category_exceptions = {'name': 'Exeption',
                                'slug': 'exeption',
                                'description': 'exeption'
                                }
    # -- Card data --
    data_cards_category_exceptions = [{'name': 'Basic Example',
                                       'card_type': 'T',
                                       'content': 'try:'
                                                  '   <code>'
                                                  'except <exception>:'
                                                  '   <code>'},
                                      {'name': 'Complex Example',
                                       'card_type': 'T',
                                       'content': 'try:'
                                                  '     <code_1>'
                                                  'except <exception_a>:'
                                                  '     <code_2_a>'
                                                  'except <exception_b>:'
                                                  '     <code_2_b>'
                                                  ' else:'
                                                  '     <code_2_c>'
                                                  'finally:'
                                                  '     <code_3>'},
                                      {'name': '"else" block',
                                       'card_type': 'T',
                                       'content': "Code inside the 'else' block will only be executed if 'try' block had no exception"},
                                      {'name': '"finally" block',
                                       'card_type': 'T',
                                       'content': "Code inside the 'finally' block will always be executed."},
                                      {'name': 'Catching Exceptions',
                                       'card_type': 'T',
                                       'content': 'except <exception>:'
                                                  'except <exception> as <name>:'
                                                  'except (<exception>, ...):'
                                                  'except (<exception>, ...) as <name>:'},
                                      {'name': 'Raise Exceptions',
                                       'card_type': 'T',
                                       'content': 'raise <exception>'
                                                  'raise <exception>()'
                                                  'raise <exception>(<el> [, ...])'},
                                      {'name': 'Useful built-in exceptions',
                                       'card_type': 'T',
                                       'content': "raise TypeError('Argument is of wrong type!')"
                                                  "raise ValueError('Argument is of right type but inappropriate value!')"
                                                  "raise RuntimeError('None of above!')"},
                                      ]
    data_cards_category_oop = [{'name': 'Class',
                                'card_type': 'T',
                                'content': 'A class is a collection of objects. A class contains the blueprints or the prototype from which the objects are being created. It is a logical entity that contains some attributes and methods. '},
                               {'name': 'Objects',
                                'card_type': 'T',
                                'content': 'The object is an entity that has a state and behavior associated with it. It may be any real-world object like a mouse, keyboard, chair, table, pen, etc. Integers, strings, floating-point numbers, even arrays, and dictionaries, are all objects. More specifically, any single integer or any single string is an object.'},
                               {'name': 'Inheritance',
                                'card_type': 'T',
                                'content': 'Inheritance is the capability of one class to derive or inherit the properties from another class. The class that derives properties is called the derived class or child class and the class from which the properties are being derived is called the base class or parent class. The benefits of inheritance are:'},
                               {'name': 'Types of Inheritance',
                                'card_type': 'T',
                                'content': 'Single Inheritance:'
                                           'Single-level inheritance enables a derived class to inherit '
                                           'characteristics from a single-parent class. '
                                           'Multilevel Inheritance:'
                                           'Multi-level inheritance enables a derived class to inherit properties from an immediate parent class which in turn inherits properties from his parent class.'
                                           'Hierarchical Inheritance:'
                                           'Hierarchical level inheritance enables more than one derived class to inherit properties from a parent class.'
                                           'Multiple Inheritance:'
                                           'Multiple level inheritance enables one derived class to inherit properties from more than one base class.'},
                               {'name': 'Polymorphism',
                                'card_type': 'T',
                                'content': 'Polymorphism simply means having many forms. For example, we need to determine if the given species of birds fly or not, using polymorphism we can do this using a single function.'},
                               {'name': 'Encapsulation',
                                'card_type': 'T',
                                'content': 'Encapsulation is one of the fundamental concepts in object-oriented programming (OOP). It describes the idea of wrapping data and the methods that work on data within one unit.'},
                               {'name': 'Data Abstraction',
                                'card_type': 'T',
                                'content': 'It hides the unnecessary code details from the user. '
                                           'Also,  when we do not want to give out sensitive parts of our code '
                                           'implementation and this is where data abstraction came.'}
                               ]

    def setUp(self):
        self.user_login_data = {
            'username': 'allex',
            'password': 'rootroot'
        }

        self.client.login(**self.user_login_data)
        self.user = get_user(self.client)
        return super().setUp()


class CategoriesViewTestCase(BaseTest):

    def add_cards_to_category(self, category, cards):
        cards_obj = []
        for card in cards:
            new_card = Card.objects.create(author=self.user, **card)
            print(new_card)
            # todo fix bag. crashing test when start in in group
            new_card.category.add(category)
            cards_obj.append(new_card)
        return cards_obj

    def test_can_view_add_category(self):
        response = self.client.get(reverse('add_category'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category/add_category.html')

    def test_add_category(self):
        response = self.client.post(reverse('add_category'), self.data_category_oop)
        category_obj = Category.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('categories'))
        self.assertEqual(category_obj.name, self.data_category_oop["name"])

    def test_category(self):
        category_obj = Category.objects.create(author=self.user, **self.data_category_oop)
        cards_oop = self.add_cards_to_category(category_obj, self.data_cards_category_oop)
        response = self.client.get(reverse('category', args=(self.data_category_oop['slug'],)))
        self.assertEqual(response.context['category'], category_obj)
        self.assertListEqual(list(response.context['cards']), cards_oop)


class CardViewTestCase(BaseTest):

    def setUp(self):
        super(CardViewTestCase, self).setUp()
        self.category_obj = Category.objects.create(author=self.user, **self.data_category_oop)
        self.user2 = User.objects.filter(pk=6).first()
        Category.objects.create(author=self.user2, **self.data_category_exceptions)
        return super().setUp()

    def test_can_view_add_cards(self):
        response = self.client.get(reverse('add_card',  args=(self.data_category_oop['slug'],)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/add_card.html')

    def test_view_form_add_cards(self):
        response = self.client.get(reverse('add_card',  args=(self.data_category_oop['slug'],)))

        self.assertEqual(response.status_code, 200)

        form_card_types = response.context['form']['card_type']

        self.assertEqual(len(form_card_types), 3)
        self.assertEqual(form_card_types[0].data.get('value'), "W")
        self.assertEqual(form_card_types[1].data.get('value'), "T")
        self.assertEqual(form_card_types[2].data.get('value'), "")

        form_categories = response.context['form']['category']

        self.assertEqual(len(form_categories), 2)
        self.assertEqual(form_categories[0].data.get('value'), '')
        self.assertEqual(form_categories[1].data.get('value').value, self.category_obj.pk)

    def test_add_card(self):
        card_data = self.data_cards_category_oop[0]
        card_data['category'] = self.category_obj.pk

        response = self.client.post(reverse('add_card', args=(self.data_category_oop['slug'],)), card_data)
        card = Card.objects.first()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(card.name, card_data['name'])
        self.assertEqual(card.card_type, card_data['card_type'])
        self.assertEqual(len(card.category.all()), 1)
        self.assertEqual(card.category.all()[0], self.category_obj)
        self.assertEqual(card.count_shows, 0)
        self.assertEqual(card.author, self.user)
