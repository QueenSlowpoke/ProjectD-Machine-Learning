from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.contrib.auth import authenticate

class RegistrationForm(UserCreationForm):
    Job_title_choices = [('Developer', 'Developer'),
                         ('Designer', 'Designer'),
                         ('Office', 'Office')
                        ]
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={ 'placeholder': 'example@gmail.com'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))
    firstname = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'John'}))
    lastname = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Doe'}))
    jobtitle = forms.ChoiceField(choices=Job_title_choices, widget=forms.RadioSelect(attrs={}))


    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'jobtitle', 'password1', 'password2')

    
    
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.firstname = self.cleaned_data['firstname']
        user.lastname = self.cleaned_data['lastname']
        user.email = self.cleaned_data['email']

        if User.objects.filter(email=self.cleaned_data['email']).count() != 0:
            raise forms.ValidationError("Email already exists")
        
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Invalid Email or Password')
        return super(LoginForm, self).clean(*args, **kwargs)