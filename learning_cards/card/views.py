import datetime
import json

from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib import messages

from .models import Category, Card, Box, Statistic, Profile
from .forms import AddCard, AddCategory, AddBox, RegisterUserForm, LoginUserForm, UserProfile, ShareCategories
from random import randint

from .utils import encrypt, decrypt

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register/register.html'
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data.get('username'),
                        email=form.cleaned_data.get("email"),
                        password=form.cleaned_data.get('password1'))
            profile = Profile(user=user)
            profile.save()
            return redirect('login')
        else:
            content = {'form': form}
            return render(request, 'register/register.html', content)


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
def share_categories(requests):
    if requests.method == "POST":
        form = ShareCategories(requests.POST, user=requests.user)
        if form.is_valid():
            category = ','.join(map(lambda x: str(x.pk), form.cleaned_data.get('category')))
            category_url = encrypt(category)
            url = reverse('shared_categories', args=[category_url])
        return render(requests, 'category/share_categories.html', {'link': url})
    else:
        form = ShareCategories(user=requests.user)
    title = 'Chose category to share'
    submit_title = "Make Share link"
    content = {'form': form,
               'title': title,
               "submit_title": submit_title}

    return render(requests, 'category/share_categories.html', content)


def shared_category(requests, crypt_categories):
    cat_id = decrypt(crypt_categories).split(',')
    categories = Category.objects.filter(id__in=cat_id).all()
    return render(requests, "category/categories.html", {"categories": categories}) # todo refactor HTML to correct render for unauthorized user


# todo make function
def shared_category_card(requests, crypt_category):
    cat_id = decrypt(crypt_category).split(',')
    category = Category.objects.filter(id__in=cat_id).all()
    pass


@login_required()
def add_card(requests, category_slug):
    category = Category.objects.get(author=requests.user, slug=category_slug)
    if requests.method == "POST":
        form = AddCard(requests.POST, user=requests.user)
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
        form = AddCard(user=requests.user)
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
        form = AddBox(requests.POST, user=requests.user, instance=box)
        if form.is_valid():
            form.save()
            return redirect('boxes')
    else:
        box = Box.objects.get(author=requests.user, slug=box_slug)
        form = AddBox(user=requests.user, instance=box)
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
        form = AddBox(requests.POST, user=requests.user)
        if form.is_valid():
            box = form.save(commit=False)
            box.author = requests.user
            box.save()
            box.category.set(form.cleaned_data.get('category'))
            box.save()
            return redirect('boxes')
    else:
        form = AddBox(user=requests.user)
    content = {'form': form,
               'title': title,
               "submit_title": submit_title}
    return render(requests, 'box/add_box.html', content)


@login_required()
def learn(requests):
    title = "Сhoose a box to learn"
    profile = requests.user.profile
    if requests.method == "POST":
        form = UserProfile(requests.POST, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfile(instance=profile)
    learned_today = requests.user.profile.get_learned_today
    cards_to_repeat = requests.user.profile.get_cards_to_repeat
    statistics = profile.get_statistic(7)
    boxes = requests.user.box_set.all()
    content = {"form": form,
               "boxes": boxes,
               'title': title,
               'learned': len(learned_today),
               'repeat': len(cards_to_repeat),
               'statistics': json.dumps(statistics)}
    return render(requests, "learn/learn.html", content)


def learning(requests, box_slug):
    extra_learning = False
    limit = requests.user.profile.day_limit
    today_learned = requests.user.profile.get_learned_today
    if len(today_learned) >= limit:
        extra_learning = True
    if requests.method == "POST":
        learning_cards = requests.POST.getlist("id")
        learned_card_id = requests.POST.get("learned")
        learning_cards = list(Card.objects.filter(id__in=learning_cards).all())
        if learned_card_id:
            for i, card in enumerate(learning_cards):
                if int(card.pk) == int(learned_card_id):
                    card.add_count_shows()
                    card.save()
                    today_learned.append(card)
                    learning_cards.pop(i)
        if len(today_learned) == limit and not extra_learning:
            return redirect('congratulations')
    else:
        learning_cards = requests.user.profile.get_learning_cards(box_slug)
    try:
        card = learning_cards[randint(0, len(learning_cards)-1)]
    except ValueError as err:
        messages.info(requests, message=f"The box is empty! Please add cards to make you day goal!")
        return redirect('learn')
    data = {"cards": learning_cards,
            "learning_card":card}
    return render(requests, "learn/learning.html", data)


def repeat(requests):
    next_card = ''
    card = ''
    if requests.method == "POST":
        learning_cards = requests.POST.getlist("id")
        learned_card_id = requests.POST.get("learned")
        card = requests.POST.get("learning")
        learning_cards = list(Card.objects.filter(id__in=learning_cards).all())
        if learned_card_id:
            for i, card in enumerate(learning_cards):
                if int(card.pk) == int(learned_card_id):
                    card.add_count_shows()
                    card.save()
                    statistic = Statistic(card_id=card, user_id=requests.user)
                    statistic.save()
                    learning_cards.pop(i)
        if len(learning_cards) == 0:
            messages.info(requests, message=f"Congratulation! You repeat you goal cards!")
            return redirect('learn')
    else:
        learning_cards = requests.user.profile.get_cards_to_repeat
    try:
        while not next_card or next_card == card:
            next_card = learning_cards[randint(0, len(learning_cards) - 1)]
    except ValueError as err:
        messages.info(requests, message=f"You repeat you goal cards!")
        return redirect('learn')
    data = {"cards": learning_cards,
            "learning_card": next_card}
    return render(requests, "learn/learning.html", data)



def congratulations(requests):
    title = "Congratulations! Goal for the day accomplished!"
    return render(requests, "learn/сongratulations.html", {'title': title})
