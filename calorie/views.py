import base64
import io
import matplotlib. pyplot as plt
from matplotlib import use
from django.http import HttpResponse
from matplotlib.figure import Figure

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

    # Data preparation
    labels = ['Calories', 'Protein', 'Carbs', 'Fats', 'Cholestrol', 'Iron', 'Calcium', 'Sodium', 'Magnesium']
    values = [data.calories, data.protein, data.carbs, data.fats, data.cholestrol, data.iron, data.calcium, data.sodium, data.magnesium]

    # Generate the bar chart
    plt.bar(labels, values, color=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'orange', 'violet'])
    plt.title('Nutrition Overview - Bar Chart')
    plt.ylabel('Amount')
    plt.xlabel('Nutrients')
    plt.xticks(rotation=45)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    bar_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Generate the pie chart
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet', 'cyan'])
    plt.title('Nutrition Overview - Pie Chart')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    pie_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Generate the line chart
    plt.plot(labels, values, marker='o', color='blue', linestyle='--')
    plt.title('Nutrition Overview - Line Chart')
    plt.ylabel('Amount')
    plt.xlabel('Nutrients')
    plt.xticks(rotation=45)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    line_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Generate the donut chart
    colors = ['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet', 'cyan']
    wedges, texts, autotexts = plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title('Nutrition Overview - Donut Chart')
    plt.gca().add_artist(plt.Circle((0, 0), 0.70, fc='white'))  # Add a white circle in the center to create a donut effect

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    donut_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return render(request, "calorie/meal_detail.html", {
        "data": data,
        "bar_chart": bar_chart,
        "pie_chart": pie_chart,
        "line_chart": line_chart,
        "donut_chart": donut_chart
    })