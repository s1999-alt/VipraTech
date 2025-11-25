from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import stripe

from .models import Product, Order

stripe.api_key = settings.STRIPE_SECRET_KEY


def signup_view(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('/')
  else:
    form = UserCreationForm()
  return render(request, 'signup.html', {'form': form})


def login_view(request):
  if request.method == 'POST':
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      return redirect('/')
  else:
    form = AuthenticationForm()
  return render(request, 'login.html', {'form': form})


def logout_view(request):
  logout(request)
  return redirect('/')


def index(request):
  products = Product.objects.all()
  orders = Order.objects.filter(user=request.user, paid=True) if request.user.is_authenticated else []

  context = {
    "products": products,
    "orders": orders,
    "stripe_public_key": settings.STRIPE_PUBLIC_KEY
  }
  return render(request, "index.html", context)


@login_required
def create_checkout_session(request):
  if not request.user.is_authenticated:
    messages.warning(request, "Please login to continue.")
    return redirect(f"/login/?next=/")
  
  if request.method != 'POST':
    return redirect("/")
  
  product_id = request.POST.get("product_id")
  quantity = int(request.POST.get("quantity", 1))

  try:
    product = Product.objects.get(id=product_id)
  except Product.DoesNotExist:
    messages.error(request, "Invalid product.")
    return redirect("/")
  
  session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    line_items=[{
        "price_data": {
            "currency": "inr",
            "product_data": {"name": product.name},
            "unit_amount": int(product.price * 100),
        },
        "quantity": quantity,
    }],
    mode="payment",
    success_url=request.build_absolute_uri("/success") + "?session_id={CHECKOUT_SESSION_ID}",
    cancel_url=request.build_absolute_uri("/cancel"),
  )

  return redirect(session.url, code=303)


def success_view(request):
  session_id = request.GET.get("session_id")
  if not session_id:
    return redirect("/")
  
  try:
    session = stripe.checkout.Session.retrieve(session_id)
  except Exception:
      messages.error(request, "Invalid session.")
      return redirect("/")
  
  if session.payment_status != "paid":
    messages.error(request, "Payment failed or incomplete.")
    return redirect("/")

  if Order.objects.filter(stripe_session_id=session_id).exists():
    return redirect("/")
  
  line_items = stripe.checkout.Session.list_line_items(session_id)
  item = line_items.data[0]

  product_name = item.description
  quantity = item.quantity

  try:
    product = Product.objects.get(name=product_name)
  except Product.DoesNotExist:
    messages.error(request, "Product not found after payment.")
    return redirect("/")
  
  total_amount = product.price * quantity

  with transaction.atomic():
    Order.objects.create(
        user=request.user,
        product=product,
        quantity=quantity,
        total_amount=total_amount,
        stripe_session_id=session_id,
        paid=True,
    )
  return redirect("/")


def cancel_view(request):
  context = {
    "message": "Your payment was canceled or failed. Please try again.",
  }
  return render(request, "cancel.html", context)






