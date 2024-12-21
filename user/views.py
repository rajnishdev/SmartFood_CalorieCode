from user import utils
from django.shortcuts import render,redirect
from django.urls import path
from .import forms
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import UserProfile
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.http import HttpResponse


# Create your views here.
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate user account
        user.save()
        messages.success(request, 'Email verified successfully. You can now log in.')
        return redirect('login')
    else:
        return HttpResponse('Invalid verification link.')


def signup(request):
    if request.method == "POST":
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  
            user.is_active = False  # Deactivate account until email is verified
            user.save()

            # Send verification email
            utils.send_verification_email(user, request)

            messages.success(request, 'Account successfully created. Please check your email to verify your account.')
            return redirect('login')
        else:
            return render(request, 'user/register.html', {'form': form})
    else:
        form = forms.RegistrationForm()
    return render(request, 'user/register.html', {'form': form})


def signout(request):
    messages.success(request, "You have been successfully logged out!")
    logout(request)
    return render(request,'user/landing.html')


def landing(request):
    return render(request, 'user/landing.html')
