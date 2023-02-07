from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import timedelta, datetime


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
    time_last_show = models.DateTimeField(auto_now=True)
    time_next_show = models.DateTimeField(auto_now_add=True)
    count_shows = models.IntegerField(default=0) # if count_shows == -1 ie mean that word is leard for ever.
    category = models.ManyToManyField('Category')

    def get_absolute_url(self):
        return reverse('card', kwargs={'card_id': self.pk, 'category_slug': self.category.all()[0].slug})

    def _set_next_show_time(self):
        repeat_cycle = { 1: timedelta(hours=2),
                         2: timedelta(hours=12),
                         3: timedelta(hours=24),
                         4: timedelta(hours=48),
                         5: timedelta(hours=168),
                         6: timedelta(hours=720),
                        }
        self.time_next_show = datetime.now() + repeat_cycle.get(self.count_shows)

    def add_count_shows(self):
        self.count_shows += 1
        if self.count_shows >= 7:
            self.count_shows = -1 # if count_shows == -1 it means that word is learned forever.
        self._set_next_show_time()


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

    def get_absolute_url(self):
        return reverse('update_box', kwargs={'box_slug': self.slug})

    def get_cards(self):
        cards = []
        for category in self.category.all():
            cards += category.card_set.filter(time_next_show__lt=datetime.now())
        return cards

    def get_categories(self):
        return self.category.all()

    def __str__(self):
        return self.name


class UserSetting(models.Model):
    max_value = 100
    min_value = 1
    message_int_value = 'Number must be from {} to {}'.format(min_value, max_value)
    user_setting = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    number_of_cards = models.PositiveIntegerField(default=5,
                                                  validators=[MaxValueValidator(max_value, message=message_int_value),
                                                              MinValueValidator(min_value, message=message_int_value)])
