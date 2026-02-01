from django.urls import path
from .views import membership

urlpatterns = [
    path('', membership, name='membership'),
]
