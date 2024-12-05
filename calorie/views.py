from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.auth.decorators import login_required
from .models import DailyGoal, Image
from .forms import DailyGoalForm, ImageUploadForm
from django.shortcuts import get_object_or_404

# Create your views here.
@login_required
def home(request):
    data = DailyGoal.objects.filter(user = request.user).first()
    context = {
        'data': data
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

            # Make prediction here (pre-process the image and make prediction with your model)

            return redirect('home')  # Replace with your desired success URL
    else:
        form = ImageUploadForm()

    return render(request, 'calorie/upload_image.html', {'form': form})