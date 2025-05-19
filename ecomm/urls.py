from django.urls import path
from . import views

urlpatterns = [
   
    path('',views.home, name='home'),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path('register/',views.register, name='register'),
    path('login/',views.login, name='login'),
]
