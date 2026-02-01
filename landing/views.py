from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    return render(request, 'Home.html')

def login_view(request):
    return render(request, 'landing/login.html')

def register_view(request):
    return render(request, 'landing/register.html')

def health_check(request):
    return JsonResponse({
        'status': 'OK',
        'message': 'Servidor Django corriendo correctamente',
        'app': 'EduPlatform'
    })