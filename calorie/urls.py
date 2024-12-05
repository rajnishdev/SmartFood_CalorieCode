from django.urls import path
from . import views

urlpatterns = [
    path("",views.home,name='home'),
    path("edit_daily_goals/", views.edit_daily_goals, name="edit_daily_goals"),
    path("upload_image/", views.upload_image, name="upload_image")
]