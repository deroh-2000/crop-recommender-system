from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
import pickle
import numpy as np
from .models import SoilData
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import Settings

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def recommend(request):
    return render(request, 'recommend.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            subject = f"New Contact Message from {name}"
            body = f"Sender Name: {name}\nSender Email: {email}\n\nMessage:\n{message}"

            try:
                send_mail(
                    subject,
                    body,
                    "jumahderick806@gmail.com",  # Must match EMAIL_HOST_USER
                    ["jumahderick806@gmail.com",],  # Change this to your recipient
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent successfully!")
            except Exception as e:
                print(f"Error sending email: {e}")  # Debugging
                messages.error(request, f"Error sending email: {e}")

        else:
            messages.error(request, "All fields are required!")

    return render(request, "contact.html")

def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Change to your desired page after login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("login")

    return render(request, "register.html")

@login_required
def dashboard(request):
    if request.user.is_authenticated:
        recommendations = SoilData.objects.filter(user=request.user)

        # Get total recommendations
        total_recommendations = recommendations.count()

        # Get total saved reports (adjust if reports are stored differently)
        total_reports = recommendations.count()  # Placeholder

        # Get most recommended crop
        most_recommended_crop = (
            recommendations.values('recommended_crop')
            .annotate(count=Count('recommended_crop'))
            .order_by('-count')
            .first()
        )

        context = {
            'recommendations': recommendations,
            'total_recommendations': total_recommendations,
            'total_reports': total_reports,
            'most_recommended_crop': most_recommended_crop['recommended_crop'] if most_recommended_crop else "None",
        }
        return render(request, 'dashboard.html', context)

    return render(request, 'dashboard.html', {})


# Load the trained model
with open('crop_model.pkl', 'rb') as file:
    model = pickle.load(file)

def predict_crop(request):
    if request.method == "POST":
        print("Form Data Received:", request.POST)  # Debugging

        try:
            # Extract input values
            nitrogen = float(request.POST.get('nitrogen', 0))
            phosphorus = float(request.POST.get('phosphorus', 0))
            potassium = float(request.POST.get('potassium', 0))
            ph = float(request.POST.get('ph', 0))
            rainfall = float(request.POST.get('rainfall', 0))
            temperature = float(request.POST.get('temperature', 0))

            # Prepare data for prediction
            input_data = np.array([[nitrogen, phosphorus, potassium, ph, rainfall, temperature]])
            print("Input Data for Prediction:", input_data)  # Debugging

            # Perform prediction
            predicted_crop = model.predict(input_data)[0]
            print("Predicted Crop:", predicted_crop)  # Debugging

            # Save recommendation in the database
            recommendation = SoilData.objects.create(
                user=request.user if request.user.is_authenticated else None,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                ph=ph,
                rainfall=rainfall,
                temperature=temperature,
                recommended_crop=predicted_crop
            )
            recommendation.save()
            print("Recommendation saved successfully.")  # Debugging

            # Redirect to dashboard or display result
            return render(request, 'recommend.html', {'predicted_crop': predicted_crop})

        except Exception as e:
            print("Error during prediction:", e)
            return render(request, 'recommend.html', {'predicted_crop': "Error in prediction. Please check input values."})

    return render(request, 'recommend.html')

def generate_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="crop_report.pdf"'

    # Create a PDF canvas
    p = canvas.Canvas(response)

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Crop Recommender System Report")

    # Fetch soil data
    soil_data = SoilData.objects.all()

    # Table Headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 750, "Nitrogen | Phosphorus | Potassium | pH | Rainfall | Temperature | Crop")

    # Table Data
    y = 730
    p.setFont("Helvetica", 10)
    for data in soil_data:
        record = f"{data.nitrogen}       | {data.phosphorus}        | {data.potassium}       | {data.ph}    | {data.rainfall}      | {data.temperature}       | {data.recommended_crop}"
        p.drawString(50, y, record)
        y -= 20

    # Close and return the PDF
    p.showPage()
    p.save()
    return response
