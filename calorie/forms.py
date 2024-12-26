from django import forms
from .models import DailyGoal, Image

class DailyGoalForm(forms.ModelForm):
    class Meta:
        model = DailyGoal
        fields = ['weight', 'height', 'lifestyle']
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter weight in kg'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter height in cm'}),
            'lifestyle': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'calories': 'Daily Calorie Goal (kcal)',
            'protein': 'Daily Protein Goal (g)',
            'carbs': 'Daily crabs Goal (g)',
            'fats': 'Daily fats Goal (g)',
        }



class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
        
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', "type": "file"}),
        }
