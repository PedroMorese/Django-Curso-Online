import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, authenticate, login
from django.db import IntegrityError


ALLOWED_ROLES = {"CLIENTE", "PROFESOR", "ADMIN"}


def _has_field(model, name):
    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False


@csrf_exempt
def register_view(request):
    """Registro de usuario (JSON POST).

    Body JSON esperado: {"email": "..", "password": "..", "first_name": "..", "last_name": "..", "role": "CLIENTE|PROFESOR|ADMIN"}

    Nota: usa el user model activo (get_user_model). Para simplificar la integración con frontend separado, esta vista está
    exenta de CSRF — en producción recomiendo usar token CSRF o un endpoint protegido y forzar HTTPS.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body or b"{}")
    except Exception:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    email = payload.get("email")
    password = payload.get("password")
    first_name = payload.get("first_name", "")
    last_name = payload.get("last_name", "")
    role = (payload.get("role") or "").upper()

    if not email or not password or not role:
        return JsonResponse({"detail": "Missing required fields (email, password, role)"}, status=400)

    if role not in ALLOWED_ROLES:
        return JsonResponse({"detail": f"Invalid role. Allowed: {', '.join(ALLOWED_ROLES)}"}, status=400)

    User = get_user_model()
    username_field = getattr(User, "USERNAME_FIELD", "username")

    create_kwargs = {}
    # set identifier for create_user according to USERNAME_FIELD
    create_kwargs[username_field] = email
    # always set email if field exists
    if _has_field(User, "email"):
        create_kwargs["email"] = email
    if _has_field(User, "first_name"):
        create_kwargs["first_name"] = first_name
    if _has_field(User, "last_name"):
        create_kwargs["last_name"] = last_name
    # if user model defines a role field, pass it
    if _has_field(User, "role"):
        create_kwargs["role"] = role

    try:
        user = User.objects.create_user(**create_kwargs, password=password)
    except TypeError:
        # fallback for create_user implementations that don't accept kwargs order
        try:
            user = User.objects.create_user(email, email, password)
            if _has_field(User, "first_name"):
                user.first_name = first_name
            if _has_field(User, "last_name"):
                user.last_name = last_name
            if _has_field(User, "role"):
                setattr(user, "role", role)
            user.save()
        except IntegrityError:
            return JsonResponse({"detail": "User with that email already exists"}, status=400)
        except Exception as e:
            return JsonResponse({"detail": f"Registration failed: {str(e)}"}, status=500)
    except IntegrityError:
        return JsonResponse({"detail": "User with that email already exists"}, status=400)
    except Exception as e:
        return JsonResponse({"detail": f"Registration failed: {str(e)}"}, status=500)

    # ensure role is set if create_user didn't accept it
    if _has_field(User, "role") and getattr(user, "role", None) != role:
        setattr(user, "role", role)
        user.save()

    return JsonResponse({"id": user.pk, "email": getattr(user, "email", None), "role": getattr(user, "role", None)}, status=201)


@csrf_exempt
def login_view(request):
    """Login de usuario (JSON POST). Crea sesión con django.contrib.auth.login.

    Body JSON esperado: {"email": "..", "password": ".."}
    Responde con información básica del usuario si autenticación correcta.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body or b"{}")
    except Exception:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        return JsonResponse({"detail": "Missing credentials"}, status=400)

    User = get_user_model()
    username_field = getattr(User, "USERNAME_FIELD", "username")

    user = None
    # try direct authenticate using provided identifier
    try:
        user = authenticate(request, username=email, password=password)
    except Exception:
        user = None

    # If authentication failed and the USERNAME_FIELD is not email, try lookup
    if user is None and username_field != "email":
        try:
            candidate = User.objects.filter(email__iexact=email).first()
            if candidate:
                user = authenticate(request, username=getattr(candidate, username_field), password=password)
        except Exception:
            user = None

    if user is None:
        return JsonResponse({"detail": "Invalid credentials"}, status=401)

    if not getattr(user, "is_active", True):
        return JsonResponse({"detail": "User account is disabled"}, status=403)

    # login sets the session cookie
    login(request, user)

    return JsonResponse({"detail": "Login successful", "id": user.pk, "email": getattr(user, "email", None), "role": getattr(user, "role", None)})


@csrf_exempt
def logout_view(request):
    """Logout de usuario. Cierra la sesión actual."""
    from django.contrib.auth import logout
    
    if request.method == "POST":
        logout(request)
        return JsonResponse({"detail": "Logout successful"})
    
    return JsonResponse({"detail": "Method not allowed"}, status=405)
