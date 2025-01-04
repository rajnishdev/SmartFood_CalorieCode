from django.urls import path
from . import views

urlpatterns = [
    path("",views.home,name='home'),
    path("goals/", views.goals, name="goals"),
    path("edit_daily_goals/", views.goals, name="edit_daily_goals"),
    path("upload_image/", views.upload_image, name="upload_image"),
    path("meal_detail/", views.meal_detail, name="meal_detail"),
    path("profile/", views.profile, name="profile"),
    path("generate-report/<str:format>/", views.generate_report, name="generate_report"),
    path('visualization/', views.visualization, name='visualization'),
]