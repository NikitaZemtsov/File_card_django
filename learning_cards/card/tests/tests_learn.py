from django.contrib.auth import get_user
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from pprint import pprint

from card.models import User, Category, Card, Box


class BaseTest(TestCase):

    # -- Category data --
    data_category_oop = {'name': 'OOP',
                         'slug': 'oop',
                         'description': 'oop'
                         }
    data_category_exceptions = {'name': 'Exeption',
                                'slug': 'exeption',
                                'description': 'exeption'
                                }

    #-- Card data --
    data_cards_category_exceptions = [{'name': 'Basic Example',
                                       'content': 'try:'
                                                  '   <code>'
                                                  'except <exception>:'
                                                  '   <code>'},
                                      {'name': 'Complex Example',
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
                                       'content': "Code inside the 'else' block will only be executed if 'try' block had no exception"},
                                      {'name': '"finally" block',
                                       'content': "Code inside the 'finally' block will always be executed."},
                                      {'name': 'Catching Exceptions',
                                       'content': 'except <exception>:'
                                                  'except <exception> as <name>:'
                                                  'except (<exception>, ...):'
                                                  'except (<exception>, ...) as <name>:'},
                                      {'name': 'Raise Exceptions',
                                       'content': 'raise <exception>'
                                                  'raise <exception>()'
                                                  'raise <exception>(<el> [, ...])'},
                                      {'name': 'Useful built-in exceptions',
                                       'content': "raise TypeError('Argument is of wrong type!')"
                                                  "raise ValueError('Argument is of right type but inappropriate value!')"
                                                  "raise RuntimeError('None of above!')"},
                                      ]
    data_cards_category_oop = [{'name': 'Class ',
                                'content': 'A class is a collection of objects. A class contains the blueprints or the prototype from which the objects are being created. It is a logical entity that contains some attributes and methods. '},
                               {'name': 'Objects',
                                'content': 'The object is an entity that has a state and behavior associated with it. It may be any real-world object like a mouse, keyboard, chair, table, pen, etc. Integers, strings, floating-point numbers, even arrays, and dictionaries, are all objects. More specifically, any single integer or any single string is an object.'},
                               {'name': 'Inheritance',
                                'content': 'Inheritance is the capability of one class to derive or inherit the properties from another class. The class that derives properties is called the derived class or child class and the class from which the properties are being derived is called the base class or parent class. The benefits of inheritance are:'},
                               {'name': 'Types of Inheritance',
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
                                'content': 'Polymorphism simply means having many forms. For example, we need to determine if the given species of birds fly or not, using polymorphism we can do this using a single function.'},
                               {'name': 'Encapsulation',
                                'content': 'Encapsulation is one of the fundamental concepts in object-oriented programming (OOP). It describes the idea of wrapping data and the methods that work on data within one unit.'},
                               {'name': 'Data Abstraction',
                                'content': 'It hides the unnecessary code details from the user. '
                                           'Also,  when we do not want to give out sensitive parts of our code '
                                           'implementation and this is where data abstraction came.'}
                               ]

    def setUp(self):
        self.registration_url = reverse('register')
        self.login_url = reverse('login')
        self.user_registration = {
            'email': 'user@gmail.com',
            'username': 'user',
            'password1': 'rootroot',
            'password2': 'rootroot',
        }
        self.user_login = {
            'username': 'user',
            'password': 'rootroot'
        }
        self.client.post(self.registration_url, self.user_registration, format='text/html')
        self.client.login(**self.user_login)
        self.user = get_user(self.client)

        return super().setUp()

    def add_cards_to_category(self, category, cards):
        cards_obj = []
        for card in cards:
            new_card = category.card_set.create(author=self.user, **card)
            cards_obj.append(new_card)
        return cards_obj


class CategoriesViewTestCase(BaseTest):

    def setUp(self):
        super(CategoriesViewTestCase, self).setUp()
        return super().setUp()

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
        self.cards_oop = self.add_cards_to_category(category_obj, self.data_cards_category_oop)
        response = self.client.get(reverse('category', args=(self.data_category_oop['slug'],)))
        self.assertEqual(response.context['category'], category_obj)
        self.assertListEqual(list(response.context['cards']), self.cards_oop)


class CardViewTestCase(BaseTest):
    pass


class LearnViewTestCase(BaseTest):

    def setUp(self):
        super(LearnViewTestCase, self).setUp()
        self.category_oop = Category.objects.create(author=self.user, **self.data_category_oop)
        self.category_exeption = Category.objects.create(author=self.user, **self.data_category_exceptions)
        self.cards_oop = self.add_cards_to_category(self.category_oop, self.data_cards_category_oop)
        self.cards_exeption = self.add_cards_to_category(self.category_exeption, self.data_cards_category_exceptions)
        self.box_python = Box.objects.create(author=self.user, name='Python', slug='python', description="python")
        self.box_python.category.set([self.category_oop, self.category_exeption])
        return super().setUp()

    def test_can_view_learn_page(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learn/choice_box.html')

    def test_box_list(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learn/choice_box.html')
        self.assertEqual(response.context['boxes'][0], self.box_python)
        self.assertEqual(response.context['form']['day_limit'].value(), 5)
