

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import timedelta, datetime, date

from django.utils import timezone


class Card(models.Model):
    TERM = "T"
    WORD = "W"

    TYPE_OF_CARD_CHOICES = [
        (WORD, 'Word'),
        (TERM, 'Term'),
        (None, 'Choose card type'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    card_type = models.CharField(max_length=1, choices=TYPE_OF_CARD_CHOICES)
    transcription = models.TextField(blank=True)
    translate = models.TextField(blank=True)
    content = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_first_show = models.DateTimeField(null=True)
    time_last_show = models.DateTimeField(auto_now=True)
    time_next_show = models.DateTimeField(auto_now_add=True)
    count_shows = models.IntegerField(default=0)  # if count_shows == -1 ie mean that word is leard for ever.
    category = models.ManyToManyField('Category')

    def get_absolute_url(self):
        return reverse('card', kwargs={'card_id': self.pk, 'category_slug': self.category.all()[0].slug})

    def _set_next_show_time(self):
        repeat_cycle = {1: timedelta(hours=2),
                        2: timedelta(hours=12),
                        3: timedelta(hours=24),
                        4: timedelta(hours=48),
                        5: timedelta(hours=168),
                        6: timedelta(hours=720),
                        -1: timedelta(hours=0)}
        self.time_next_show = datetime.now() + repeat_cycle.get(self.count_shows)

    def _set_first_shows_time(self):
        if self.count_shows == 1:
            self.time_first_show = datetime.now()

    def add_count_shows(self):
        self.count_shows += 1
        if self.count_shows >= 7:
            self.count_shows = -1  # if count_shows == -1 it means that word is learned forever.
        self._set_next_show_time()
        self._set_first_shows_time()

    class Meta:
        ordering = ["time_create"]

    def __str__(self):
        return self.name


class Category(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, verbose_name='URL')
    description = models.CharField(max_length=255, blank=True)
    time_create = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('category', kwargs={'category_slug': self.slug})

    def __str__(self):
        return self.name


class Box(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, verbose_name='URL')
    description = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField('Category')
    cards = models.ManyToManyField('Card')

    def get_absolute_url(self):
        return reverse('update_box', kwargs={'box_slug': self.slug})

    def get_cards_learn(self):
        cards = []
        for category in self.category.all():
            cards += category.card_set.filter(count_shows__gt=0)
        return cards

    def get_categories(self):
        return self.category.all()

    def __str__(self):
        return self.name


class Profile(models.Model):
    max_value = 100
    min_value = 1
    message_int_value = 'Number must be from {} to {}'.format(min_value, max_value)

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    day_limit = models.IntegerField(default=5,
                                    validators=[MaxValueValidator(max_value, message=message_int_value),
                                                MinValueValidator(min_value, message=message_int_value)])

    @property
    def get_learned_today(self):
        cards = Card.objects.filter(author=self.user) \
            .filter(time_first_show__date=date.today())
        return cards

    @property
    def get_cards_to_repeat(self):
        cards = Card.objects.filter(author=self.user) \
            .filter(time_next_show__lt=datetime.now()) \
            .filter(count_shows__gt=0)
        return cards

    def get_learning_cards(self, box_slug):
        box = self.user.box_set.filter(slug=box_slug).get()
        category = box.category.all()
        left = self.day_limit - len(self.get_learned_today)
        if len(left) == 0:
            left = self.day_limit
        cards = Card.objects.filter(category__in=category).filter(count_shows=0).all()[:left]
        return cards


class Statistic(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    card_id = models.ForeignKey(Card, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
