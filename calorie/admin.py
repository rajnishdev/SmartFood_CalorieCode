from django.contrib import admin
from .models import DailyGoal, Image

@admin.register(DailyGoal)
class DailyGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'calories', 'protein', 'updated_at')
    search_fields = ('user__username',)


admin.site.register(Image)