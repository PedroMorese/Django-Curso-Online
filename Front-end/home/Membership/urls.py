from django.urls import path
from .view import membership

urlpatterns = [
    path('', membership, name='membership'),
]
