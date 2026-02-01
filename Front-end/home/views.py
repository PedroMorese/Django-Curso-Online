
from django.shortcuts import render


def home(request):
	"""Renderiza el template principal de la home/dashboard."""
	return render(request, 'Home.html')


def register(request):
	"""Renderiza la home pero indica que debe abrirse el modal de registro."""
	return render(request, 'Home.html', {'open_register': True})


def login(request):
	"""Renderiza la home pero indica que debe abrirse el modal de login."""
	return render(request, 'Home.html', {'open_login': True})
