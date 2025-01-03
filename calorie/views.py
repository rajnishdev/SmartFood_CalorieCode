import base64
import io
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from matplotlib import use
from django.http import HttpResponse
from matplotlib.figure import Figure
import numpy as np
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.auth.decorators import login_required
from .models import DailyGoal, Image, NutritionData
from .forms import DailyGoalForm, ImageUploadForm
from django.shortcuts import get_object_or_404
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image as PilImage
from . import utils
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
# Create your views here.

@login_required
def home(request):
    user_meals = NutritionData.objects.filter(user=request.user).order_by('-id')  # Fetch meals in reverse order
    paginator = Paginator(user_meals, 1)  # Show one meal at a time

    # Get the current page number from the session or default to 1
    page_number = request.session.get('current_page', 1)
    action = request.POST.get('action')

    # Adjust page number based on action
    if action == 'prev' and page_number > 1:
        page_number -= 1  # Decrease page number for 'prev'
    elif action == 'next' and page_number < paginator.num_pages:
        page_number += 1  # Increase page number for 'next'

    # Save the current page in session
    request.session['current_page'] = page_number

    # Get the current meal
    current_meal = paginator.page(page_number).object_list.first()

    # Format the current date as 'Jan 02 2025'
    today_date = timezone.now().strftime('%b %d %Y')

    context = {
        'current_meal': current_meal,
        'has_previous': page_number > 1,
        'has_next': page_number < paginator.num_pages,
        'today_date': today_date,
    }

    return render(request, 'calorie/home.html', context)

def calculate_bmi(weight, height):
    height_m = height / 100
    return weight / (height_m * height_m)

def get_recommended_values(weight, height, lifestyle, gender):
    bmi = calculate_bmi(weight, height)
    base_calories = {
        'S': {'M': 2000, 'F': 1800},
        'M': {'M': 2300, 'F': 2000},
        'A': {'M': 2600, 'F': 2200},
        'V': {'M': 3000, 'F': 2400}
    }

    calories = base_calories[lifestyle][gender]
    
    if bmi > 25:  # Weight loss
        calories *= 0.85
    elif bmi < 18.5:  # Weight gain
        calories *= 1.15

    return {
        'calories': int(calories),
        'protein': int(calories * 0.20 / 4),  # 20% of calories from protein
        'carbs': int(calories * 0.50 / 4),    # 50% of calories from carbs
        'fats': int(calories * 0.30 / 9)      # 30% of calories from fats
    }

@login_required
def goals(request):
    daily_goal = DailyGoal.objects.filter(user=request.user).first()
    is_initial_setup = daily_goal is None

    if request.method == 'POST':
        form = DailyGoalForm(request.POST, instance=daily_goal)
        if form.is_valid():
            goal = form.save(commit=False)
            
            # Calculate recommended values
            recommendations = get_recommended_values(
                float(goal.weight),
                float(goal.height),
                goal.lifestyle,
                request.user.userprofile.gender
            )
            
            # Set the calculated values
            goal.calories = recommendations['calories']
            goal.protein = recommendations['protein']
            goal.carbs = recommendations['carbs']
            goal.fats = recommendations['fats']
            goal.user = request.user
            goal.save()
            
            return redirect('home')
    else:
        form = DailyGoalForm(instance=daily_goal)
    
    return render(request, 'calorie/goals.html', {
        'form': form,
        'is_initial_setup': is_initial_setup
    })

'''
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
'''


def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.user = request.user
            image_instance.save()

            # Check the image size (in bytes)
            image_file = request.FILES['image']
            image_size = image_file.size  # Size in bytes

            if image_size > 10 * 1024 * 1024:  # 10 MB in bytes
                messages.error(request, "The uploaded image is too large. Please upload an image smaller than 10 MB.")
                return redirect('upload_image')  # Redirect to the same page to show the error message

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
            nutrition_data = utils.fetch_nutrition(f"{1} {class_name}")
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

def generate_chart(chart_type, labels, values, **kwargs):
    plt.figure()
    if chart_type == "bar":
        plt.bar(labels, values, color=kwargs.get("colors", "blue"))
        plt.title(kwargs.get("title", "Bar Chart"))
    elif chart_type == "pie":
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=kwargs.get("colors"))
        plt.title(kwargs.get("title", "Pie Chart"))
    elif chart_type == "line":
        plt.plot(labels, values, marker='o', linestyle='--', color=kwargs.get("color", "blue"))
        plt.title(kwargs.get("title", "Line Chart"))
    elif chart_type == "donut":
        wedges, texts, autotexts = plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=kwargs.get("colors"))
        plt.gca().add_artist(plt.Circle((0, 0), 0.70, fc='white'))
        plt.title(kwargs.get("title", "Donut Chart"))

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()
    return chart_data

# Function to handle large images
def handle_large_image(image_path, max_size=(1024, 1024)):
    pil_image = PilImage.open(image_path)
    pil_image.thumbnail(max_size)  # Resize to fit within max dimensions
    pil_image.save(image_path)  # Overwrite with resized version
    return pil_image


def meal_detail(request):
    # Fetch the latest NutritionData object
    data = NutritionData.objects.filter(user=request.user).last()
    if not data:
        messages.error(request, "No nutrition data available.")
        return redirect("upload_image")

    # Labels and values
    labels = ['Calories', 'Protein', 'Carbs', 'Fats', 'Cholesterol', 'Iron', 'Calcium', 'Sodium', 'Magnesium']
    raw_values = [
        data.calories, data.protein, data.carbs, data.fats, data.cholestrol,
        data.iron, data.calcium, data.sodium, data.magnesium
    ]

    # Replace None, NaN, or any invalid values with 0 and ensure values are valid floats
    values = []
    for val in raw_values:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            values.append(0)
        else:
            values.append(float(val))  # Ensure it's a float value

    # Debug: Log values before charting
    print("Debug - Processed Chart Values:", values)

    # Check for any zeros or NaNs in the values before chart generation
    # If any value is zero, we will set it to a small value (e.g., 1) to avoid division by zero
    safe_values = [1e-6 if val == 0 or np.isnan(val) else val for val in values]

    # Generate charts with safe values
    try:
        bar_chart = generate_chart("bar", labels, safe_values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Bar Chart")
        pie_chart = generate_chart("pie", labels, safe_values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Pie Chart")
        line_chart = generate_chart("line", labels, safe_values, color='blue', title="Nutrition Overview - Line Chart")
        donut_chart = generate_chart("donut", labels, safe_values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Donut Chart")
    except Exception as e:
        print("Error during chart generation:", str(e))
        messages.info(request, "Error generating charts.")
        return redirect("upload_image")

    return render(request, "calorie/meal_detail.html", {
        "data": data,
        "bar_chart": bar_chart,
        "pie_chart": pie_chart,
        "line_chart": line_chart,
        "donut_chart": donut_chart
    })


@login_required
def profile(request):
    """
    View for the user's profile page.
    """
    return render(request, 'calorie/profile.html', {'user': request.user})

