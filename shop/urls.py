from django.urls import path
from . import views


urlpatterns = [
  path('', views.index, name='index'),
  path('signup/', views.signup_view, name='signup'),
  path('login/', views.login_view, name='login'),
  path('logout/', views.logout_view, name='logout'),

  path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
  path('success', views.success_view, name='success'),
  path('cancel', views.cancel_view, name='cancel'),
]
