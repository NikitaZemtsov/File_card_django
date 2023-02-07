import datetime

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages

from .models import Category, Card, Box, UserSetting
from .forms import AddCard, AddCategory, AddBox, RegisterUserForm, LoginUserForm, AddUserSettings
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

@login_required()
def categories(requests):
    categories = Category.objects.filter(author=requests.user).all()
    return render(requests, "category/categories.html", {"categories": categories})

@login_required()
def category(requests, category_slug):
    category = Category.objects.get(author=requests.user, slug=category_slug)
    data = {'cards': category.card_set.all(),
            'category': category,
            }
    return render(requests, "category/category.html", data)

@login_required()
def card_repr(requests, card_id, category_slug):
    card = Card.objects.get(author=requests.user, pk=card_id)
    return render(requests, "card/card_repr.html", {"card": card})



@login_required()
def add_card(requests, category_slug):
    category = Category.objects.get(author=requests.user, slug=category_slug)
    if requests.method == "POST":
        form = AddCard(requests.POST)
        if form.is_valid():
                data = form.cleaned_data
                category = data.pop('category')
                card = Card(**data)
                card.author = requests.user
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


@login_required()
def add_category(requests):
    if requests.method == "POST":
        form = AddCategory(requests.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = requests.user
            category.save()
            return redirect('categories')
    else:
        form = AddCategory()
    title = 'Add category'
    submit_title = "Add"
    content = {'form': form,
               'title': title,
               "submit_title": submit_title}
    return render(requests, 'category/add_category.html', content)

@login_required()
def update_category(requests, category_slug):
    category = Category.objects.get(author=requests.user, slug=category_slug)
    if requests.method == "POST":
        form = AddCategory(requests.POST, instance=category)
        if form.is_valid():
            form.save()
        return redirect('categories')
    else:
        form = AddCategory(instance=category)
    title = 'Update category'
    submit_title = "Update"
    content = {'form': form,
               'title': title,
               "submit_title": submit_title,
               'category': category}
    return render(requests, 'category/add_category.html', content)

@login_required()
def delete_category(requests, category_slug):
    category = Category.objects.get(author=requests.user, slug=category_slug)
    category.delete()
    return redirect('categories')

@login_required()
def boxes(requests):
    title = "Boxes"
    boxes = Box.objects.filter(author=requests.user)
    content = {"boxes": boxes,
               'title': title,
               }
    return render(requests, "box/boxes.html", content)

@login_required()
def update_box(requests, box_slug):
    title = 'Update box'
    submit_title = "Update"
    box = Box.objects.get(author=requests.user, slug=box_slug)
    if requests.method == "POST":
        form = AddBox(requests.POST, instance=box)
        if form.is_valid():
            form.save()
            return redirect('boxes')
    else:
        box = Box.objects.get(author=requests.user, slug=box_slug)
        form = AddBox(instance=box)
    content = {'title': title,
               "form": form,
               "submit_title": submit_title
               }
    return render(requests, "box/add_box.html", content)

@login_required()
def add_box(requests):
    title = 'Add Box'
    submit_title = "Add"
    if requests.method == "POST":
        form = AddBox(requests.POST)
        if form.is_valid():
            box = form.save(commit=False)
            box.author = requests.user
            box.save()
            return redirect('boxes')
    else:
        form = AddBox()
    content = {'form': form,
               'title': title,
               "submit_title": submit_title}
    return render(requests, 'box/add_box.html', content)

@login_required()
def learn(requests):
    title = "Choose to study"
    user_settings = UserSetting.objects.get(user_setting=requests.user)
    if requests.method == "POST":
        form = AddUserSettings(requests.POST, instance=user_settings)
        if form.is_valid():
            form.save()
    else:
        form = AddUserSettings(instance=user_settings)
    learned_today = Card.objects.filter(author=requests.user)\
                                        .filter(time_last_show__date=datetime.date.today())\
                                        .filter(count_shows__gt=0)
    cards_to_repeat = Card.objects.filter(author=requests.user)\
                                        .filter(time_next_show__lt=datetime.datetime.now())\
                                        .filter(count_shows__gt=0)
    boxes = Box.objects.filter(author=requests.user)
    content = {"form": form,
               "boxes": boxes,
               'title': title,
               'learned': len(learned_today),
               'repeat': len(cards_to_repeat)
               }
    return render(requests, "learn/choice_box.html", content)


def learning(requests, box_slug):
    user_settings = UserSetting.objects.get(user_setting=requests.user)
    limit = user_settings.number_of_cards
    today_learned = len(Card.objects.filter(author=requests.user) \
                     .filter(time_last_show__date=datetime.date.today()) \
                     .filter(count_shows__gt=0))
    if requests.method == "POST":
        learning_cards = requests.POST.getlist("id")
        learned_card_id = requests.POST.get("learned")
        if learned_card_id:
            learned_card = Card.objects.get(id=learned_card_id)
            learned_card.add_count_shows()
            learned_card.save()
            i = 0
            for card in learning_cards:
                if card == learned_card_id:
                    learning_cards.pop(i)
                i += 1
        if today_learned == limit:
            return redirect('congratulations')
        learning_cards = list(Card.objects.filter(id__in=learning_cards).all())
    else:
        learning_cards = Box.objects.get(slug=box_slug).get_cards()[:limit]
    try:
        card =  learning_cards[randint(0, len(learning_cards)-1)]
    except ValueError as err:
        messages.info(requests, message=f"You dont have cards to learn! Please add cards or repeat exist")
        return redirect('learn')
    data = {"cards": learning_cards,
            "learning_card":card}
    return render(requests, "learn/learning.html", data)


def congratulations(requests):
    title = "Congratulations! Goal for the day accomplished!"
    return render(requests, "learn/сongratulations.html", {'title': title})
