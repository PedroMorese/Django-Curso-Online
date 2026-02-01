
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import json


def home(request):
	"""Renderiza el template principal de la home/dashboard."""
	return render(request, 'Home.html')


def register(request):
	"""Renderiza la home pero indica que debe abrirse el modal de registro."""
	return render(request, 'Home.html', {'open_register': True})


def login(request):
	"""Renderiza la home pero indica que debe abrirse el modal de login."""
	return render(request, 'Home.html', {'open_login': True})


def register_api(request):
	"""API local para crear usuario desde el formulario (POST).

	Acepta JSON o form-encoded. Responde JSON con status 201 si se crea.
	"""
	if request.method != 'POST':
		return JsonResponse({'detail': 'Method not allowed'}, status=405)

	# parse JSON body if present
	data = {}
	if request.content_type == 'application/json':
		try:
			data = json.loads(request.body or b'{}')
		except Exception:
			return JsonResponse({'detail': 'Invalid JSON'}, status=400)
	else:
		data = request.POST.dict()

	email = data.get('email')
	password = data.get('password')
	first_name = data.get('first_name', '')
	last_name = data.get('last_name', '')

	if not email or not password:
		return JsonResponse({'detail': 'Missing email or password'}, status=400)

	User = get_user_model()
	try:
		# Build kwargs respecting the model's USERNAME_FIELD so we don't rely on
		# a positional 'username' argument that some user managers require.
		username_field = getattr(User, 'USERNAME_FIELD', 'username')
		# prefer an explicit value from the form, else fall back to email or a safe placeholder
		username_value = data.get(username_field) or data.get('username') or (email.split('@')[0] if email else None)
		create_kwargs = {}
		if username_value is not None:
			create_kwargs[username_field] = username_value
		# include email if it's a separate field (i.e. USERNAME_FIELD != 'email')
		if username_field != 'email' and email:
			create_kwargs['email'] = email
		# pass names via extra fields so managers that accept **extra_fields receive them
		if first_name:
			create_kwargs['first_name'] = first_name
		if last_name:
			create_kwargs['last_name'] = last_name
		# finally call create_user with password and constructed kwargs
		user = User.objects.create_user(password=password, **create_kwargs)
		# if the model stores role as an attribute, set a default
		if hasattr(user, 'role'):
			try:
				user.role = 'CLIENTE'
			except Exception:
				pass
		user.save()
	except IntegrityError:
		return JsonResponse({'detail': 'User with that email already exists'}, status=400)
	except Exception as e:
		return JsonResponse({'detail': f'Registration failed: {str(e)}'}, status=500)

	return JsonResponse({'id': user.pk, 'email': getattr(user, 'email', None)}, status=201)
