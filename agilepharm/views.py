from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
import requests
from .models import Store


# --- Static pages ---
def home(request):
    return render(request, 'agile/home.html')


def relief(request):
    return render(request, 'agile/relief.html')


def futurepharm(request):
    return render(request, 'agile/futurepharm.html')


def blog(request):
    return render(request, 'agile/blog.html')


def career(request):
    return render(request, 'agile/career.html')


# --- Shop and search ---
def shop(request):
    """
    Display all products with optional category filter and search query.
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    products = Store.objects.all()

    if category:
        products = products.filter(category__iexact=category)

    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    context = {
        'products': products,
        'active_category': category,
        'query': query
    }
    return render(request, 'agile/shop.html', context)


def search_products(request):
    """
    Dedicated search results page.
    """
    query = request.GET.get("q", "").strip()
    products = Store.objects.none()

    if query:
        products = Store.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, "agile/search.html", {
        "products": products,
        "query": query
    })


# --- Cart operations ---
def add_to_cart(request, product_id):
    """
    Add a product to the cart stored in the session.
    """
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart(request, product_id):
    """
    Remove a product completely from the cart.
    """
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')


def update_cart(request, product_id, action):
    """
    Update the quantity of a product in the cart.
    Action can be 'increase' or 'decrease'.
    """
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


def cart_view(request):
    """
    Display the cart page with product details and totals.
    """
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Store, id=product_id)
        subtotal = float(product.price) * quantity
        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })
        total += subtotal

    return render(request, "agile/cart.html", {"items": items, "total": total})


# --- Checkout with Paystack ---
def checkout(request):
    """
    Handle checkout and initialize Paystack payment.
    """
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Store, id=product_id)
        subtotal = float(product.price) * quantity
        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })
        total += subtotal

    if request.method == "POST":
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
        if res.get('status'):
            return redirect(res['data']['authorization_url'])
        else:
            return HttpResponse(f"Payment initialization failed: {res.get('message')}")

    return render(request, "agile/checkout.html", {"items": items, "total": total})


def payment_success(request):
    """
    Verify Paystack payment and clear cart on success.
    """
    reference = request.GET.get('reference')
    if not reference:
        return HttpResponse("No payment reference provided.")

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
    res = response.json()

    if res.get('status') and res['data'].get('status') == 'success':
        request.session['cart'] = {}  # clear cart after successful payment
        return render(request, "agile/payment_success.html")
    else:
        return HttpResponse("Payment verification failed.")
