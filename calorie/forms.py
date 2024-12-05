from django import forms
from .models import DailyGoal, Image

class DailyGoalForm(forms.ModelForm):
    class Meta:
        model = DailyGoal
        fields = ['calories', 'protein', 'carbs', 'fats']
        widgets = {
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2000'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 50'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 250g'}),
            'fats': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 70g'}),
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
