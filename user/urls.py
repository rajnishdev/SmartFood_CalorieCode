from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/',auth_views.LoginView.as_view(template_name="user/login.html"),name='login'),
    path('signup/',views.signup,name='signup'),
    path('signout/',views.signout,name='signout'),
    
    # login redirects to landing page
    path('landing/', views.landing, name='landing'),

    #verify email
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify-email'),
]