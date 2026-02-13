"""
URLs UX de Membresías.
"""

from django.urls import path
from . import views

app_name = 'membership_ux'

urlpatterns = [
    path('', views.membership_plans, name='plans'),
    path('subscribe/<slug:plan_slug>/', views.subscribe, name='subscribe'),
    path('checkout/<slug:plan_slug>/', views.checkout, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
]
