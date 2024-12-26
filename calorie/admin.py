from django.contrib import admin
from .models import DailyGoal, Image, NutritionData

@admin.register(DailyGoal)
class DailyGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'calories', 'lifestyle')  # Removed 'updated_at'
    search_fields = ('user__username',)

@admin.register(NutritionData)
class NutritionDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'class_name', 'calories')
    search_fields = ('user__username','class_name')

admin.site.register(Image)
