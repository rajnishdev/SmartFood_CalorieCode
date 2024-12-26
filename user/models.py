from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices)
    calorie_goal = models.IntegerField(default=2000)
    nutrient_goal = models.TextField(default='')

    def __str__(self):
        return self.user.username

# Remove the existing signal and update with this one
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check if profile already exists
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'name': instance.username,
                'age': 25,
                'gender': 'M',
                'calorie_goal': 2000,
                'nutrient_goal': ''
            }
        )