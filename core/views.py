from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def registro(request):
    return render(request, 'registro.html') 