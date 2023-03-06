from django.urls import path, include, re_path
from .views import *

urlpatterns = [
        path('categories/', categories, name="categories"),
        path('category/<slug:category_slug>', category,  name="category"),
        path('category/<slug:category_slug>/update', update_category,  name="update_category"),
        path('category/<slug:category_slug>/delete', delete_category,  name="delete_category"),
        path('category/<slug:category_slug>/card/<int:card_id>/', card_repr, name="card"),
        path('category/<slug:category_slug>/add_card', add_card, name="add_card"),
        path('share_categories', share_categories, name="share_categories"),
        path('shared_link/<crypt_categories>', shared_category, name="shared_categories"),
        path('shared_link/cards/<crypt_category>', shared_category_card, name="shared_category_card"),
        path('add_category', add_category, name="add_category"),
        path('box/', boxes, name="boxes"),
        path('box/<slug:box_slug>', update_box,  name="update_box"),
        path('add_box', add_box,  name="add_box"),
        path('', learn, name="learn"),
        path('learning/<slug:box_slug>', learning, name="learning"),
        path('repeat/', repeat, name="repeat"),
        path('congratulations/', congratulations,  name="congratulations"),
        path('login/', LoginUser.as_view(), name='login'),
        path('register/', RegisterUser.as_view(), name='register'),
        path('logout/', logout_user, name='logout'),
]

