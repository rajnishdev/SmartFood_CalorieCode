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



class NutritionData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField(default=0)
    protein = models.PositiveIntegerField(default=0)
    carbs = models.PositiveIntegerField(default=0)
    fats = models.PositiveIntegerField(default=0)
    cholestrol = models.PositiveIntegerField(default=0)
    iron = models.PositiveIntegerField(default=0)
    calcium = models.PositiveIntegerField(default=0)
    sodium = models.PositiveIntegerField(default=0)
    magnesium = models.PositiveIntegerField(default=0)
    phosphorus = models.PositiveIntegerField(default=0)
    zinc = models.PositiveIntegerField(default=0)
    vitaminb12 = models.PositiveIntegerField(default=0)
    folic_acid = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.class_name} nutrition"

