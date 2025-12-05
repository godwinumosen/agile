from django.urls import path
from . import views

urlpatterns = [
    # Home / Shop page
    path('', views.shop, name='shop'),
    path('shop/', views.shop, name='shop'),

    # Cart actions
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("update-cart/<int:product_id>/<str:action>/", views.update_cart, name="update_cart"),

    # Cart and checkout pages
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout, name="checkout"),

    # Payment success callback
    path('payment-success/', views.payment_success, name='payment_success'),
    
]
