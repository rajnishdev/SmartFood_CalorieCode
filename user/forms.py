from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Replace with your custom user model if applicable

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    name = forms.CharField(max_length=100)
    age = forms.IntegerField()
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = forms.ChoiceField(choices=gender_choices)  # Use ChoiceField for choices

    class Meta:
        model = User  # Ensure this is the correct model
        fields = ["email", "username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = ""  # Remove label for all fields

