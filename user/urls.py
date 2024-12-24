from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name="user/login.html", 
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('landing/', views.landing, name='landing'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify-email'),
]
