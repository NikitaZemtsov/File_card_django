from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


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
    count_shows = models.IntegerField(default=0)
    category = models.ManyToManyField('Category')

    def get_absolute_url(self):
        return reverse('card', kwargs={'card_id': self.pk, 'category_slug': self.category.all()[0].slug})

    def add_count_shows(self):
        self.count_shows += 1


    def learn_now(self):
        pass

    def set_next_show_time(self):
        pass

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
            cards += category.card_set.all()
        return cards

    def __str__(self):
        return self.name