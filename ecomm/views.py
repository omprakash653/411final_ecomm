from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.db import IntegrityError, DatabaseError
from django.contrib import messages
from django.shortcuts import redirect
from .models import Contact,Product,Cart,Order
from django.contrib.auth import authenticate, login, logout
import re
from django.core.mail import send_mail
from django.conf import settings
import random
from django.utils.timezone import now
import razorpay

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


###########################################################user
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

@csrf_protect  # This ensures CSRF protection is explicitly applied (optional if middleware is enabled)
def user_login(request):
    if request.method == "POST":
        uname = request.POST.get('uname', '').strip()
        upass = request.POST.get('upass', '').strip()

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

otp_storage = {}

######################################### reset password functionality
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            otp_storage[email] = {"otp": otp, "time": now()}  # Save OTP & timestamp

            # Send OTP via email
            subject = "Password Reset OTP - Shopping Kart"
            message = f"""
            Hello {user.username},

            You requested a password reset. Use the OTP below to proceed:
            
            🔢 Your OTP: {otp}

            This OTP is valid for 10 minutes.

            If you didn't request this, please ignore this email.

            Regards,
            Shopping Kart Team
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

            messages.success(request, "OTP has been sent to your email.")
            return redirect("verify_otp")

        except User.DoesNotExist:
            messages.error(request, "Email not registered!")
            return redirect("forgot_password")

    return render(request, "forgot_password.html")


def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        otp_entered = request.POST.get("otp")

        if email in otp_storage:
            otp_data = otp_storage[email]
            otp_correct = otp_data["otp"]

            if str(otp_entered) == str(otp_correct):
                messages.success(request, "OTP verified! Set a new password.")
                return redirect("reset_password")
            else:
                messages.error(request, "Invalid OTP! Please try again.")
                return redirect("verify_otp")
        else:
            messages.error(request, "OTP expired or invalid.")
            return redirect("forgot_password")

    return render(request, "verify_otp.html")

def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("reset_password")

        if len(new_password) < 6 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
            messages.error(request, "Password must be at least 6 characters long and contain both letters and numbers.")
            return redirect("reset_password")

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Clear OTP after successful reset
            otp_storage.pop(email, None)

            messages.success(request, "Password reset successful! You can log in now.")
            return redirect("login")

        except User.DoesNotExist:
            messages.error(request, "Error resetting password. Please try again.")

    return render(request, "reset_password.html")



# def product(request):
#     p=Product.objects.filter(is_active=True)
#     # print(p)
#     context={}
#     context['data']=p
#     return render(request, "product.html")


####################################################### product views
def product(request):
    p = Product.objects.filter(is_active=True)
    print(p)  # Check if the queryset is returning products
    context = {'data': p}
    return render(request, "product.html", context)

def product_detail(request,pid):
    p=Product.objects.filter(id=pid)
    # print(p)
    context = {'data': p}
    return render(request,'product_details.html',context)



###################################### Filters for products
from django.db.models import Q

def catfilter(request, cv):
    # print(cv)
    q1 = Q(category=cv)  
    q2 = Q(is_active=True)

    p = Product.objects.filter(q1 & q2)
    # print(p)
    context = {'data': p}
    return render(request, 'product.html', context)


def sortfilter(request,sv):
    # print(sv,type(sv))
    if sv=='1':
        # p=Product.objects.order_by('-price')
        # context['data']=p
        t=('-price')
    else:
        # p=Product.objects.order_by('price')
        # context['data']=p
        t=('price')
    
    p=Product.objects.order_by(t).filter(is_active=True)
    # print(p)
    context = {'data': p}
    return render(request,'product.html',context)

def pricefilter(request):
    mn=request.GET['min']
    mx=request.GET['max']

    # print(mn)
    # print(mx)
    q1=Q(price__gte= mn)
    q2=Q(price__lte= mx)
    q3=Q(is_active=True)

    p=Product.objects.filter(q1 &q2&q3)
    # print(p)
    context = {'data': p}
    return render(request,'product.html',context)

def srcfilter(request):
    s = request.GET.get('search', '').strip() 
    pname=Product.objects.filter(name__icontains=s)
    pdet=Product.objects.filter(pdetails__icontains=s)
    alldata=pname.union(pdet)
    # print(alldata)
    context={}
    if alldata.count()==0:
        context['errmsg']='Product Not Found'
    
    context['data']=alldata
    return render(request,'product.html',context)



###################### add to cart functionality
def add_to_cart(request, pid):
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(id=pid)

        cart_item, created = Cart.objects.get_or_create(uid=user, pid=product)

        if not created:
            messages.error(request, "Product already in cart.")
        else:
            messages.success(request, "Product added successfully!")

        return redirect("cart")

    return redirect("login")

def cart(request):
    user_cart = Cart.objects.filter(uid=request.user.id)
    total_price = sum(item.pid.price * item.qty for item in user_cart)

    return render(request, "cart.html", {"data": user_cart, "total": total_price, "n": len(user_cart)})


def updateqty(request,x,cid):
    c=Cart.objects.filter(id=cid)
    # print(c[0].qty)
    q=c[0].qty
    if x=='1':
        q=q+1
    elif q>1: 
        q=q-1

    c.update(qty=q)
    return redirect('/cart')

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/cart')


def placeorder(request):
    c=Cart.objects.filter(uid=request.user.id)
    for i in c:
        a=i.pid.price*i.qty
        o=Order.objects.create(uid=i.uid,pid=i.pid,qty=i.qty,amt=a)
        o.save()
        i.delete()
    return redirect('/fetchorder')
    
def fetchorder(request):
    o=Order.objects.filter(uid=request.user.id)
    context={}
    s=0
    for i in o:
        s=s+i.amt
    context['data']=o
    context['total']=s
    context['n']=len(o)
    return render(request,'placeorder.html',context)


##################
def makepayment(request):
    client = razorpay.Client(auth=("rzp_test_0cZOKkv2JT3kMN", "2JknC0N7GWmm1I9Lj4R908AB"))
    total_amount = sum(order.amt for order in Order.objects.filter(uid=request.user.id))
    
    payment = client.order.create({"amount": total_amount * 100, "currency": "INR", "receipt": "order_rcptid_11"})
    return render(request, "pay.html", {"payment": payment})

def paymentsuccess(request):
    total_amount = sum(order.amt for order in Order.objects.filter(uid=request.user.id))
    return render(request, "paymentsuccess.html", {"total_amount": total_amount})

