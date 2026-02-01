
from django.urls import path
from .views import home, register, login, register_api

urlpatterns = [
	path('', home, name='home'),
	path('register/', register, name='register'),
	path('login/', login, name='login'),
	path('register-submit/', register_api, name='register-submit'),
]
