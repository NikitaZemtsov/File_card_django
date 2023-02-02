from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.messages import get_messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import Category, Card, Box
from .forms import AddCard, AddCategory, AddBox, RegisterUserForm, LoginUserForm
from random import randint


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register/register.html'
    success_url = reverse_lazy('login')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'register/login.html'

    def get_success_url(self):
        return reverse_lazy('learn')

def logout_user(requests):
    logout(requests)
    return redirect('login')


def categories(requests):
    categories = Category.objects.all()
    return render(requests, "category/categories.html", {"categories": categories})


def category(requests, category_slug):
    category = Category.objects.get(slug=category_slug)
    data = {'cards': category.card_set.all(),
            'category': category,
            }
    return render(requests, "category/category.html", data)


def card_repr(requests, card_id, category_slug):
    card = Card.objects.get(pk=card_id)
    return render(requests, "card/card_repr.html", {"card": card})


def add_card(requests, category_slug):
    category = Category.objects.get(slug=category_slug)
    if requests.method == "POST":
        form = AddCard(requests.POST)
        if form.is_valid():
                data = form.cleaned_data
                category = data.pop('category')
                card = Card(**data)
                card.save()
                card.category.add(category)
                card.save()
                return redirect('category', category_slug)
    else:
        form = AddCard(initial={'category': category})
    title = 'Add card'
    content = {'form': form,
               'title': title,
               'category': category}
    return render(requests, 'card/add_card.html', content)


def add_category(requests):
    if requests.method == "POST":
        form = AddCategory(requests.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = AddCategory()
    title = 'Add category'
    content = {'form': form,
               'title': title}
    return render(requests, 'category/add_category.html', content)


def boxes(requests):
    title = "Boxes"
    boxes = Box.objects.all()
    content = {"boxes": boxes,
               'title': title,
               }
    return render(requests, "box/boxes.html", content)


def update_box(requests, box_slug):
    title = 'Update box'
    submit_title = "Update"
    box = Box.objects.get(slug=box_slug)
    if requests.method == "POST":
        form = AddBox(requests.POST, instance=box)
        form.save()
        return redirect('boxes')
    else:
        box = Box.objects.get(slug=box_slug)
        form = AddBox(instance=box)
        content = {'title': title,
                   "form": form,
                   "submit_title": submit_title
                   }
    return render(requests, "box/add_box.html", content)


def add_box(requests):
    title = 'Add Box'
    submit_title = "Update"
    if requests.method == "POST":
        form = AddBox(requests.POST)
        if form.is_valid():
            form.save()
            return redirect('boxes')
    else:
        form = AddBox()
    content = {'form': form,
               'title': title,
               "submit title": submit_title}
    return render(requests, 'box/add_box.html', content)


def learn(requests):
    title = "Choose to study"
    boxes = Box.objects.all()
    content = {"boxes": boxes,
               'title': title,
               }
    return render(requests, "learn/choice_box.html", content)


def learning(requests, box_slug):
    if requests.method == "POST":
        learning_cards = requests.POST.getlist("id")
        learned_card_id = requests.POST.get("learned")
        if learned_card_id:
            learned_card = Card.objects.get(id=learned_card_id)
            learned_card.add_count_shows()
            # learned_card.save()
            i = 0
            for card in learning_cards:
                if card == learned_card_id:
                    learning_cards.pop(i)
                i += 1
            if len(learning_cards) == 0:
                return redirect('congratulations')
        learning_cards = list(Card.objects.filter(id__in=learning_cards).all())
    else:
        learning_cards = Box.objects.get(slug=box_slug).get_cards()
    data = {"cards": learning_cards,
            "learning_card": learning_cards[randint(0, len(learning_cards)-1)]}
    return render(requests, "learn/learning.html", data)


def congratulations(requests):
    title = "Congratulations! Goal for the day accomplished!"
    return render(requests, "learn/сongratulations.html", {'title': title})
