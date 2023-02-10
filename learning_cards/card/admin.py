from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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


class UserProfileInlineAdmin(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'
    list_display = ('day_limit', 'user')
    list_display_links = ('day_limit', 'user')


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInlineAdmin,)

class StatisticAdmin(admin.ModelAdmin):
    list_display = ('date', 'card_id', 'user_id')
    list_display_links = ('date', 'card_id', 'user_id')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Box, BoxAdmin)
admin.site.register(Statistic, StatisticAdmin)
