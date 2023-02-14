from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import *


class AddCard(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': "form-control"}))
    card_type = forms.ChoiceField(choices=Card.TYPE_OF_CARD_CHOICES,
                                  widget=forms.Select(attrs={"class": "form-control"} ))
    transcription = forms.CharField(max_length=255, required=False,
                                    widget=forms.TextInput(attrs={'class':"form-control"}))
    translate = forms.CharField(max_length=255, required=False,
                                widget=forms.TextInput(attrs={'class': "form-control"}))
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 10, 'class':"form-control"}),
                              required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                      widget=forms.Select(attrs={"class": "form-control"}))


class AddCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.widgets.TextInput(
                attrs={'class':"form-control"}
            ),
            'slug': forms.widgets.TextInput(
                attrs={'class': "form-control"}
            ),
            'description': forms.widgets.TextInput(
                attrs={'class': "form-control"}
            )
        }


class AddBox(forms.ModelForm):

    category = forms.ModelMultipleChoiceField(queryset=Category.objects.none(), widget=forms.CheckboxSelectMultiple(attrs={"class": "form-input"}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(author=self.user)

    class Meta:
        model = Box
        fields = ['name', 'slug', 'description', 'category']
        widgets = {
            'name': forms.widgets.TextInput(
                attrs={'class':"form-control"}
            ),
            'slug': forms.widgets.TextInput(
                attrs={'class': "form-control"}
            ),
            'description': forms.widgets.TextInput(
                attrs={'class': "form-control"}
            )
        }


class UserProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['day_limit']
        labels = {
            'day_limit': 'Goal for the day: '
        }
        widgets = {
            'day_limit': forms.widgets.NumberInput(
                attrs={'class': "form-input"}
            )
        }


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': "form-control"}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': "form-control"}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': "form-control"}))
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(attrs={'class': "form-control"}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': "form-control"}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': "form-control"}))
