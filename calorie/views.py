import base64
import io
import os
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
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit

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
    elif chart_type == "scatter":
        x = np.arange(len(labels))
        plt.scatter(x, values, color=kwargs.get("color", "blue"), alpha=0.7)
        plt.xticks(x, labels, rotation=45)
        plt.title(kwargs.get("title", "Scatter Plot"))
    elif chart_type == "radar":  # Add radar chart condition
        # Number of variables
        num_vars = len(labels)

        # Compute angle of each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        # Make the radar chart a circular plot
        values += values[:1]  # to close the loop
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color=kwargs.get("color", "blue"), alpha=0.25)
        ax.plot(angles, values, color=kwargs.get("color", "blue"), linewidth=2)
        ax.set_yticklabels([])  # Hide the radial labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=10)
        plt.title(kwargs.get("title", "Radar Chart"))

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
    data = NutritionData.objects.filter(user=request.user).last()
    if not data:
        request.session['visualization_available'] = False
        messages.error(request, "No nutrition data available.")
        return redirect("upload_image")

    labels = ['Calories', 'Protein', 'Carbs', 'Fats', 'Cholesterol', 'Iron', 'Calcium', 'Sodium', 'Magnesium']
    raw_values = [
        data.calories, data.protein, data.carbs, data.fats, data.cholestrol,
        data.iron, data.calcium, data.sodium, data.magnesium
    ]

    values = [float(val) if val is not None else 0 for val in raw_values]

    # Check if there is sufficient data to enable visualization
    if any(values):
        request.session['visualization_available'] = True
    else:
        request.session['visualization_available'] = False
        messages.info(request, "Insufficient data for visualization.")
        return redirect("upload_image")
    try:
        bar_chart = generate_chart("bar", labels, values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Bar Chart")
        pie_chart = generate_chart("pie", labels, values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Pie Chart")
        line_chart = generate_chart("line", labels, values, color='blue', title="Nutrition Overview - Line Chart")
        donut_chart = generate_chart("donut", labels, values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Donut Chart")
        scatter_chart = generate_chart("scatter", labels, values, color='green', title="Nutrition Overview - Scatter Plot")
        radar_chart = generate_chart("radar", labels, values, color='blue', title="Nutrition Overview - Radar Chart")  # Radar chart generation
    except Exception as e:
        print("Error during chart generation:", str(e))
        messages.error(request, "Error generating charts.")
        return redirect("upload_image")

    return render(request, "calorie/meal_detail.html", {
        "data": data,
        "bar_chart": bar_chart,
        "pie_chart": pie_chart,
        "line_chart": line_chart,
        "donut_chart": donut_chart,
        "scatter_chart":scatter_chart,
        "radar_chart": radar_chart,
    })
def visualization(request):
    # Check if visualization is available
    if not request.session.get('visualization_available', False):
        messages.error(request, "Visualization is not available.")
        return redirect("home")

    # Fetch the latest NutritionData object
    data = NutritionData.objects.filter(user=request.user).last()
    if not data:
        messages.error(request, "No nutrition data available.")
        return redirect("home")

    labels = ['Calories', 'Protein', 'Carbs', 'Fats', 'Cholesterol', 'Iron', 'Calcium', 'Sodium', 'Magnesium']
    raw_values = [
        data.calories, data.protein, data.carbs, data.fats, data.cholestrol,
        data.iron, data.calcium, data.sodium, data.magnesium
    ]

    # Prepare values for chart generation
    values = [float(val) if val is not None else 0 for val in raw_values]

    try:
        # Generate charts
        bar_chart = generate_chart("bar", labels, values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Bar Chart")
        pie_chart = generate_chart("pie", labels, values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Pie Chart")
        line_chart = generate_chart("line", labels, values, color='blue', title="Nutrition Overview - Line Chart")
        donut_chart = generate_chart("donut", labels, values, colors=['red', 'blue', 'green', 'orange', 'pink', 'yellow', 'purple', 'violet'], title="Nutrition Overview - Donut Chart")
        scatter_chart = generate_chart("scatter", labels, values, color='green', title="Nutrition Overview - Scatter Plot")
        radar_chart = generate_chart("radar", labels, values, color='blue', title="Nutrition Overview - Radar Chart")  # Radar chart generation
    except Exception as e:
        print("Error during chart generation:", str(e))
        messages.error(request, "Error generating charts.")
        return redirect("home")

    return render(request, "calorie/visualization.html", {
        "data": data,
        "bar_chart": bar_chart,
        "pie_chart": pie_chart,
        "line_chart": line_chart,
        "donut_chart": donut_chart,
        "scatter_chart":scatter_chart,
        "radar_chart": radar_chart
    })


@login_required
def profile(request):
    """
    View for the user's profile page.
    """
    return render(request, 'calorie/profile.html', {'user': request.user})

def generate_report(request, format='pdf'):
    user = request.user
    
    # Fetch user details
    user_details = {
        "name": user.username,
        "email": user.email,
    }
    
    # Fetch user's daily goal
    daily_goal = DailyGoal.objects.filter(user=user).first()
    
    # Fetch user's nutritional data
    nutrition_data = NutritionData.objects.filter(user=user).all()

    # Prepare additional context for the report
    report_context = {
        "user_details": user_details,
        "daily_goal": daily_goal,
        "nutrition_data": nutrition_data,
    }

    if format == 'pdf':
        # Ensure correct wkhtmltopdf path
        wkhtmltopdf_path = os.environ.get("pdf_path")
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # Render HTML template with the user data, daily goals, and nutrition data
        html = render_to_string('calorie/generate_report.html', report_context)

        # Convert HTML to PDF
        pdf = pdfkit.from_string(html, False, configuration=config)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="nutrition_report.pdf"'
        return response
    else:
        return HttpResponse("Invalid format", status=400)



def generate_pdf(user_details, nutrition_data):
    html_content = render_to_string('calorie/generate_report.html', {
        "user_details": user_details,
        "nutrition_data": nutrition_data
    })

    pdf_options = {
        "page-size": "A4",
        "encoding": "UTF-8",
    }
    pdf = pdfkit.from_string(html_content, False, options=pdf_options)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="nutrition_report.pdf"'
    return response
