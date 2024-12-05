from django.shortcuts import render,redirect
from django.urls import path
from .import forms
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import UserProfile
from django.contrib.auth import authenticate
from django.contrib import messages

# Create your views here.
def register(request):
    if request.method == "POST":
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Use the password1 field for setting the password
            user.set_password(form.cleaned_data['password1'])  
            user.save()
            messages.success(request, 'Account Successfully Created')
            return redirect('login')
        else:
            # If the form is invalid, return the form with errors
            return render(request, 'user/register.html', {'form': form})
    else:
        form = forms.RegistrationForm()
    return render(request, 'user/register.html', {'form': form})


def signout(request):
    logout(request)
    return render(request,'user/signout.html')


def options_view(request):
    return render(request, 'user/options.html')


def about_view(request):
    return render(request, 'user/about.html')


def learn_more_view(request):
    return render(request, 'user/learn_more.html')


def contact_view(request):
    return render(request, 'user/contact.html')
