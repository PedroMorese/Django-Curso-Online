
from django.urls import path, include
from .views import home, register, login

urlpatterns = [
	path('', home, name='home'),
	path('register/', register, name='register'),
	path('login/', login, name='login'),

	path('membership/', include('Front-end.home.Membership.urls')),
]
