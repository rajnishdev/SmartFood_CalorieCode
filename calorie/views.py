import torch

from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.auth.decorators import login_required
from .models import DailyGoal, Image, NutritionData
from .forms import DailyGoalForm, ImageUploadForm
from django.shortcuts import get_object_or_404
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image as PilImage
from . import utils
# Create your views here.

@login_required
def home(request):
    daily_goal = DailyGoal.objects.filter(user = request.user).first()
    data = NutritionData.objects.last()
    context = {
        'daily_goal': daily_goal,
        "data": data
    }
    return render(request,'calorie/home.html', context)


@login_required
def edit_daily_goals(request):
    """
    View to display and edit the user's daily calorie and protein goals.
    """
    # Get the current user's DailyGoal instance or create a new one if it doesn't exist
    daily_goal, created = DailyGoal.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Bind the form with POST data and the current instance
        form = DailyGoalForm(request.POST, instance=daily_goal)
        if form.is_valid():
            # Save the form data to the database
            form.save()
            # Redirect to home or a success page
            return redirect('home')  # Adjust 'home' to your desired redirect URL
    else:
        # Create a form instance with the current daily goal
        form = DailyGoalForm(instance=daily_goal)

    # Render the template with the form
    return render(request, 'calorie/edit_daily_goals.html', {'form': form})



def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.user = request.user
            image_instance.save()

            image_file = image_instance.image
            image_path = image_file.path
            pil_image = PilImage.open(image_path)

            # Make prediction here (pre-process the image and make prediction with your model)
            processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
            model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

            inputs = processor(images=pil_image, return_tensors="pt")
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            class_name = model.config.id2label[predicted_class_idx]

            nutrition_data = utils.fetch_nutrition(f"{len(class_name)} {class_name}")
            calories = nutrition_data["calories"]
            protein = nutrition_data["protein"]
            carbs = nutrition_data["carbs"]
            fats = nutrition_data["fats"]
            cholestrol = nutrition_data["cholestrol"]
            iron = nutrition_data["iron"]
            calcium = nutrition_data["calcium"]
            sodium = nutrition_data["sodium"]
            magnesium = nutrition_data["magnesium"]
            phosphorus = nutrition_data["phosphorus"]
            zinc = nutrition_data["zinc"]
            vitaminb12 = nutrition_data["vitaminb12"]
            folic_acid = nutrition_data["folic_acid"]

            NutritionData.objects.create(user=request.user, image=image_instance, class_name=class_name, calories=calories, protein=protein, carbs=carbs, fats=fats,cholestrol=cholestrol, iron=iron, calcium=calcium, sodium=sodium, magnesium=magnesium, phosphorus=phosphorus,zinc=zinc,vitaminb12=vitaminb12, folic_acid=folic_acid )
            return redirect('meal_detail')
    else:
        form = ImageUploadForm()

    return render(request, 'calorie/upload_image.html', {'form': form})



def meal_detail(request):
    data = NutritionData.objects.last()
    return render(request, "calorie/meal_detail.html", {"data": data})