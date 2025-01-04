from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Replace with your custom user model if applicable
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        error_messages={'required': 'Enter your email address.'}
    )
    first_name = forms.CharField(max_length=50, error_messages={"required": "Enter your first name"})
    last_name = forms.CharField(max_length=50, error_messages={"required": "Enter your last name"})
    age = forms.IntegerField(
        error_messages={'required': 'Enter your age.'}
    )
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = forms.ChoiceField(
        choices=gender_choices,
        error_messages={'required': 'Select your gender.'}
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "age", "gender", "password1", "password2"]
        error_messages = {
            'username': {
                'required': 'Please enter a username.',
                'unique': 'This username is already taken. Please choose another one.',
            },
            'password1': {
                'required': 'Please enter a password.',
            },
            'password2': {
                'required': 'Please confirm your password.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = ""  # Remove label for all fields

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        
        # Add custom password validation here if needed
        if not password1:
            raise ValidationError("Password is required.")  # Custom message if password is missing
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Check if both passwords match
        if password1 != password2:
            raise ValidationError("The two password fields must match.")  # Custom message for mismatch

        return password2

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}),
        error_messages={
            'required': 'Username is required.',
        },
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        error_messages={
            'required': 'Password is required.',
        },
    )
