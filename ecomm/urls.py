from django.urls import path
from . import views

urlpatterns = [
   
    path('',views.home, name='home'),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path('register/',views.register, name='register'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("product/", views.product, name="product"),
]
