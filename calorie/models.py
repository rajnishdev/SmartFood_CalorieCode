from django.db import models
from django.contrib.auth.models import User

class DailyGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='daily_goal')
    calories = models.PositiveIntegerField(default=2000, help_text="Daily calorie goal in kcal.")
    protein = models.PositiveIntegerField(default=50, help_text="Daily protein goal in grams.")
    carbs = models.PositiveIntegerField(default=250, help_text="Daily carbohydrate goal in grams.")
    fats = models.PositiveIntegerField(default=70, help_text="Daily fat goal in grams.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last updated timestamp.")

    def __str__(self):
        return f"{self.user.username}'s Daily Goal"


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploaded_images')

    def __str__(self):
        return self.image.name

