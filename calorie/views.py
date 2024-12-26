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
from datetime import date
from django.contrib import messages



@login_required
def edit_daily_goals(request):
    """
    View to display and edit the user's daily calorie and protein goals.
    """
    daily_goal, created = DailyGoal.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = DailyGoalForm(request.POST, instance=daily_goal)
        if form.is_valid():
            form.save()
            return redirect('daily_goals')
    else:
        form = DailyGoalForm(instance=daily_goal)

    return render(request, 'calorie/edit_daily_goals.html', {'form': form})


@login_required
def daily_goals(request):
    """
    Page to display the user's daily goals.
    """
    daily_goal = DailyGoal.objects.filter(user=request.user).first()
    return render(request, 'calorie/daily_goals.html', {'daily_goal': daily_goal})


@login_required


def log_meals(request):
    meals = NutritionData.objects.filter(user=request.user).order_by('-id')
    context = {
        'meals': meals,
        'today_date': date.today(),
    }
    return render(request, 'calorie/log_meals.html', context)



def upload_image(request):
    """
    View to upload an image, process it using a pre-trained model, and log the nutrition data.
    """
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.user = request.user
            image_instance.save()

            image_file = image_instance.image
            image_path = image_file.path
            pil_image = PilImage.open(image_path)

            # Image prediction with pre-trained model
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

            # Save nutrition data
            NutritionData.objects.create(
                user=request.user,
                image=image_instance,
                class_name=class_name,
                calories=calories,
                protein=protein,
                carbs=carbs,
                fats=fats,
                cholestrol=cholestrol,
                iron=iron,
                calcium=calcium,
                sodium=sodium,
                magnesium=magnesium,
                phosphorus=phosphorus,
                zinc=zinc,
                vitaminb12=vitaminb12,
                folic_acid=folic_acid
            )
            return redirect('log_meals')
    else:
        form = ImageUploadForm()

    return render(request, 'calorie/upload_image.html', {'form': form})


@login_required
def trends_reports(request):
    """
    Blank page for Trends and Reports.
    """
    return render(request, 'calorie/trends_reports.html')


@login_required
def recommendations(request):
    """
    Blank page for Recommendations.
    """
    return render(request, 'calorie/recommendations.html')


@login_required
def dashboard(request):
    """
    Dashboard to track meals, display the latest logged meal, and navigate through logged meals.
    """
    meals = NutritionData.objects.filter(user=request.user).order_by('-timestamp')  # Order by timestamp

    # Initialize or update current meal index in session
    if 'current_meal_index' not in request.session:
        request.session['current_meal_index'] = 0

    current_index = request.session['current_meal_index']

    if request.method == "POST":
        if 'prev' in request.POST and current_index + 1 < meals.count():
            current_index += 1  # Move to the previous meal
        elif 'next' in request.POST and current_index > 0:
            current_index -= 1  # Move to the next meal
        request.session['current_meal_index'] = current_index

    # Get the meal for the current index
    current_meal = meals[current_index] if meals.exists() else None

    context = {
        'user': request.user,
        'today_date': date.today(),
        'current_meal': current_meal,
        'has_meals': meals.exists(),
        'has_previous': current_index + 1 < meals.count(),
        'has_next': current_index > 0,
    }
    return render(request, 'calorie/dashboard.html', context)
@login_required
def profile(request):
    """
    View for the user's profile page.
    """
    return render(request, 'calorie/profile.html', {'user': request.user})
@login_required
def edit_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Update the user's first and last name
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        # Success message
        messages.success(request, 'Your profile has been updated successfully!')

        return redirect('profile')  # Redirect back to the profile page

    return render(request, 'calorie/profile.html')
def trends_and_reports(request):
    # Get today's date for filtering (without the time part)
    today = datetime.today().date()  # Only the date part
    
    # Fetch nutrition data for today
    trends = NutritionData.objects.filter(timestamp__date=today)  # This ensures we only get today's records

    # Prepare the data for plotting
    dates = []
    calories = []
    protein = []
    carbs = []
    fats = []

    if trends.exists():  # Check if we have data
        for trend in trends:
            # Use the timestamp as the label or a formatted string (e.g., date only)
            dates.append(trend.timestamp.strftime('%Y-%m-%d'))  # Format as 'YYYY-MM-DD'
            calories.append(trend.calories)
            protein.append(trend.protein)
            carbs.append(trend.carbs)
            fats.append(trend.fats)
    else:
        # If no data, set the values to empty
        dates = ["No data available"]
        calories = [0]
        protein = [0]
        carbs = [0]
        fats = [0]

    context = {
        'dates': dates,
        'calories': calories,
        'protein': protein,
        'carbs': carbs,
        'fats': fats,
        'has_data': trends.exists(),  # Indicates whether we have data to display
    }

    return render(request, 'calorie/trends_reports.html', context)