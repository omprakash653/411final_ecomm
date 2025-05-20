from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.db import IntegrityError, DatabaseError
from django.contrib import messages
from django.shortcuts import redirect
from .models import Contact
from django.contrib.auth import authenticate, login, logout
import re
from django.contrib.auth.models import User
# Create your views here.
def home(request):
    return render(request, 'home.html')


@method_decorator(csrf_protect, name='dispatch')  # Protects all methods from CSRF attacks
class ContactView(View):
    template_name = 'contact.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            name = request.POST.get('name').strip()
            contact = request.POST.get('contact').strip()
            email = request.POST.get('email').strip()
            description = request.POST.get('description')

            errors = []
            if not name:
                errors.append("Name is required.")
            if not contact.isdigit() or len(contact) < 10:
                errors.append("Enter a valid contact number (at least 10 digits).")
            if "@" not in email or "." not in email:
                errors.append("Enter a valid email address.")
            if not description:
                errors.append("Description cannot be empty.")

            if errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, self.template_name) 
            Contact.objects.create(name=name, contact=contact, email=email, description=description)

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  
        except IntegrityError:
            messages.error(request, "Database error: A duplicate entry might exist.")
        except DatabaseError:
            messages.error(request, "Database error: Please try again later.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

        return render(request, self.template_name)  

import re
from django.contrib.auth.models import User
def register(request):
    if request.method == "POST":
        try:
            uname = request.POST.get("uname")
            uemail = request.POST.get("uemail")
            upass = request.POST.get("upass")
            ucpass = request.POST.get("ucpass")

            # Validate form data
            if not uname or not uemail or not upass or not ucpass:
                messages.error(request, "All fields are required.")
                return redirect("register")

            if upass != ucpass:
                messages.error(request, "Passwords do not match.")
                return redirect("register")

            if len(upass) < 6:
                messages.error(request, "Password must be at least 6 characters long.")
                return redirect("register")

            if not re.search(r'[A-Za-z]', upass) or not re.search(r'[0-9]', upass):
                messages.error(request, "Password must contain both letters and numbers.")
                return redirect("register")

            if User.objects.filter(username=uname).exists():
                messages.error(request, "Username already taken.")
                return redirect("register")

            if User.objects.filter(email=uemail).exists():
                messages.error(request, "Email already registered.")
                return redirect("register")

            
            user = User.objects.create_user(username=uname, email=uemail, password=upass)
            user.save()
            
            # Success message and redirect to login
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")

        except IntegrityError:
            messages.error(request, "Database error. Please try again.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    return render(request, "register.html")

def user_login(request):
    if request.method == "POST":
        uname = request.POST.get('uname').strip()
        upass = request.POST.get('upass').strip()

        user = authenticate(username=uname, password=upass)
        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("/")
        else:
            messages.error(request, "Invalid credentials! Please try again.")
            return redirect("login")

    return render(request, "login.html")

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

def forgot_password(request):
    return render(request, "forgot_password.html")