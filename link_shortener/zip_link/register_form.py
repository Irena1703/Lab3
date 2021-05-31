from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Account

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label = "Username",
        max_length = 150,
        required = True,
        help_text = "150 characters or fewer. Letters, digits and @/./+/-/_ only"
        )
    email = forms.EmailField(
        label = "Email",
        required = True
    )
    gender = forms.ChoiceField(
        label = "Gender",
        choices=Account.Genders
        )
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type':'date',
        }))
    class Meta:
        model = User
        fields = ('username', 'email', 'birth_date', 'gender', 'password1', 'password2', )
