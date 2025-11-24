from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import redirect

from .models import Product, Order


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
    form = AuthenticationForm(request, data=request.data)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      return redirect('/')
  else:
    form = AuthenticationForm()
  return render(request, 'login.html', {'form': form})



def index(request):
  products = Product.objects.all()
  orders = Order.objects.filter(user=request.user, paid=True) if request.user.is_authenticated else []

  context = {
    "products": products,
    "orders": orders,
    "stripe_public_key": settings.STRIPE_PUBLIC_KEY
  }
  return render(request, "index.html", context)
