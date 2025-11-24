from django.shortcuts import render
from django.conf import settings

from .models import Product, Order




def index(request):
  products = Product.objects.all()
  orders = Order.objects.filter(user=request.user, paid=True) if request.user.is_authenticated else []

  context = {
    "products": products,
    "orders": orders,
    "stripe_public_key": settings.STRIPE_PUBLIC_KEY
  }
  return render(request, "index.html", context)
