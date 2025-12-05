from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from .models import Store
import requests

# Display all products
def shop(request):
    products = Store.objects.all()
    return render(request, 'agile/shop.html', {"products": products})

# Add item to cart
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

# Remove item from cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')

# Update quantity in cart
def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        if action == 'increase':
            cart[str(product_id)] += 1
        elif action == 'decrease':
            cart[str(product_id)] -= 1
            if cart[str(product_id)] <= 0:
                cart.pop(str(product_id))
    request.session['cart'] = cart
    return redirect('cart')

# Display cart page
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Store, id=product_id)
        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": float(product.price) * quantity
        })
        total += float(product.price) * quantity
    return render(request, "agile/cart.html", {"items": items, "total": total})

# Checkout page with Paystack integration
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')  # redirect if cart is empty

    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Store, id=product_id)
        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": float(product.price) * quantity
        })
        total += float(product.price) * quantity

    if request.method == "POST":
        # Initialize Paystack payment
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        callback_url = request.build_absolute_uri('/payment-success/')
        data = {
            "email": request.user.email,
            "amount": int(total * 100),  # Paystack expects amount in kobo
            "callback_url": callback_url,
            "metadata": {"cart": cart}
        }
        response = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers)
        res = response.json()
        if res['status']:
            return redirect(res['data']['authorization_url'])
        else:
            return HttpResponse(f"Payment initialization failed: {res.get('message')}")

    return render(request, "agile/checkout.html", {"items": items, "total": total})

# Payment success page
def payment_success(request):
    reference = request.GET.get('reference')
    if not reference:
        return HttpResponse("No payment reference provided.")

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
    res = response.json()

    if res['status'] and res['data']['status'] == 'success':
        request.session['cart'] = {}  # clear cart after successful payment
        return render(request, "agile/payment_success.html")
    else:
        return HttpResponse("Payment verification failed.")




