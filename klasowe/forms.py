from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django import forms
from django.contrib.auth.models import User
from .models import ClassCode, Event, Year


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Login',
        widget=forms.TextInput(attrs={'autofocus': True})
    )


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm


class AddClassForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name',)
        widgets = {
            'first_name': forms.TextInput(attrs={'id': 'name'}),
            'last_name': forms.TextInput(attrs={'id': 'surname'})
        }


class AddClassCodeForm(forms.ModelForm):
    class Meta:
        model = ClassCode
        fields = ('code',)
        labels = {
            'code': 'Kod i rocznik klasy'
        }
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'np. a02', 'max_length': '5', 'id': 'codeClass'})
        }


class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',)
        labels = {
            'username': 'Nazwa użytkownika'
        }
        widgets = {
            'username': forms.TextInput(attrs={'autofocus': True})
        }


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)
        widgets = {
            'email': forms.TextInput(attrs={'autofocus': True, 'type': 'email'})
        }


class NewEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'date', 'value',)
        labels = {
            'name': 'Nazwa',
            'date': 'Data',
            'value': 'Koszt na osobę'
        }
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True, 'min_length': '3', 'max_length': '50'}),
            'date': forms.TextInput(attrs={'type': 'date'}),
            'value': forms.NumberInput(attrs={'min': '0', 'max': '9999'})
        }


class NewYearForm(forms.ModelForm):
    class Meta:
        model = Year
        fields = ('year',)
        labels = {
            'year': 'Nowy rok szkolny'
        }
        widgets = {
            'year': forms.NumberInput(attrs={'autofocus': True, 'min': '2000', 'max': '2099', 'placeholder': 'RRRR'})
        }