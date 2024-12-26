from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user.models import UserProfile

class Command(BaseCommand):
    help = 'Creates missing user profiles'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.username,
                    'age': 25,
                    'gender': 'M',
                    'calorie_goal': 2000,
                    'nutrient_goal': ''
                }
            )