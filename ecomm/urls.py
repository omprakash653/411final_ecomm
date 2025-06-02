from django.urls import path
from . import views

urlpatterns = [
   
    path('',views.home, name='home'),
    path("contact/", views.ContactView.as_view(), name="contact"),

    #user
    path('register/',views.register, name='register'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),

    #products
    path("product/", views.product, name="product"),
    path("product_detail/<int:pid>/", views.product_detail, name="product_detail"),
    
    #filters
    path("catfilter/<str:cv>/", views.catfilter, name="catfilter"),
    path("sortfilter/<str:sv>/", views.sortfilter, name="sortfilter"),
    path("pricefilter/", views.pricefilter, name="pricefilter"),
    path("srcfilter/", views.srcfilter, name="srcfilter"),


    #cart
    path("addtocart/<int:pid>/", views.add_to_cart, name="addtocart"),
    path("cart/", views.cart, name="cart"),
    path("updateqty/<str:x>/<int:cid>/", views.updateqty, name="updateqty"),
    path("remove/<int:cid>/", views.remove, name="remove"),
    path("placeorder/", views.placeorder, name="placeorder"),
    path("fetchorder/", views.fetchorder, name="fetchorder"),

    path("makepayment/", views.makepayment, name="makepayment"),
    path("paymentsuccess/", views.paymentsuccess, name="payment-success"),
]
