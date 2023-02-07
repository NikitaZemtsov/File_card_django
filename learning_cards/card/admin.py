from django.contrib import admin

# Register your models here.
from .models import *


class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'card_type', 'time_create', 'time_last_show', 'time_next_show', 'count_shows')
    list_display_links = ('id', 'name')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class BoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')

class UserSettingAdmin(admin.ModelAdmin):
    list_display = ('number_of_cards',)
    list_display_links = ('number_of_cards',)


admin.site.register(Card, CardAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Box, BoxAdmin)
admin.site.register(UserSetting, UserSettingAdmin)
