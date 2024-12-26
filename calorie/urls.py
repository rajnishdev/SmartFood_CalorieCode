from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),  # Admin panel
    path('', views.dashboard, name='dashboard'),  # Dashboard as the default homepage
    path('daily_goals/', views.daily_goals, name='daily_goals'),  # Daily Goals page
    path('edit_daily_goals/', views.edit_daily_goals, name='edit_daily_goals'),  # Edit Daily Goals page
    path('log_meals/', views.log_meals, name='log_meals'),  # Log Meals page
    path('upload_image/', views.upload_image, name='upload_image'),  # Upload Image page
    path('trends_reports/', views.trends_reports, name='trends_reports'),  # Trends and Reports page
    path('recommendations/', views.recommendations, name='recommendations'),  # Recommendations page
    path('profile/', views.profile, name='profile'),  # Profile page
     path('profile/edit/', views.edit_profile, name='edit_profile'),
]
