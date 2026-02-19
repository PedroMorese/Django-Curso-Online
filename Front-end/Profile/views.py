from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.apps import apps
from django.utils import timezone
from django.views.decorators.http import require_POST


@login_required
def profile_view(request):
    UserMembership = apps.get_model('membership', 'UserMembership')
    membership = UserMembership.objects.filter(user=request.user, status='ACTIVE').first()

    if request.user.role == 'ADMIN':
        base_template = 'dashboard_admin/base_admin.html'
    elif request.user.role == 'PROFESOR':
        base_template = 'dashboard_profesor/base_profesor.html'
    else:
        base_template = 'base/base.html'

    context = {
        'membership': membership,
        'base_template': base_template,
    }
    return render(request, 'profile_view.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        email = request.POST.get('email', '')

        user = request.user
        parts = first_name.split(' ', 1)
        user.first_name = parts[0]
        if len(parts) > 1:
            user.last_name = parts[1]

        user.email = email
        user.save()

        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('profile:view')

    return redirect('profile:view')


@login_required
@require_POST
def cancel_membership(request):
    """
    Cancela TODAS las membresías activas del usuario.

    - Cambia status → CANCELLED
    - Establece end_date = ahora para que is_active devuelva False inmediatamente
    - Desactiva auto_renew
    Los permisos (acceso a cursos) se pierden al instante porque is_active
    verifica status == 'ACTIVE' AND now() <= end_date.
    """
    try:
        UserMembership = apps.get_model('membership', 'UserMembership')

        # Cancelar todas las membresías activas o pendientes del usuario
        active_memberships = UserMembership.objects.filter(
            user=request.user,
            status__in=['ACTIVE', 'PENDING']
        )

        if not active_memberships.exists():
            messages.error(request, 'No tienes una membresía activa para cancelar.')
            return redirect('profile:view')

        now = timezone.now()
        for membership in active_memberships:
            membership.status    = 'CANCELLED'
            membership.auto_renew = False
            membership.end_date  = now   # Revoca acceso inmediatamente
            membership.save(update_fields=['status', 'auto_renew', 'end_date', 'updated_at'])

        messages.success(request, 'Tu membresía ha sido cancelada. Has perdido el acceso al contenido premium.')

    except Exception as e:
        messages.error(request, f'Error al cancelar la membresía: {str(e)}')

    return redirect('profile:view')


@login_required
@require_POST
def change_password(request):
    """
    Cambia la contraseña del usuario autenticado.
    Requiere: current_password, new_password, confirm_password.
    """
    current_password = request.POST.get('current_password', '')
    new_password = request.POST.get('new_password', '')
    confirm_password = request.POST.get('confirm_password', '')

    if not current_password or not new_password or not confirm_password:
        messages.error(request, 'Todos los campos son obligatorios.')
        return redirect('profile:view')

    if not request.user.check_password(current_password):
        messages.error(request, 'La contraseña actual es incorrecta.')
        return redirect('profile:view')

    if new_password != confirm_password:
        messages.error(request, 'La nueva contraseña y su confirmación no coinciden.')
        return redirect('profile:view')

    if len(new_password) < 8:
        messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
        return redirect('profile:view')

    request.user.set_password(new_password)
    request.user.save()

    # Mantener la sesión activa tras el cambio de contraseña
    update_session_auth_hash(request, request.user)

    messages.success(request, 'Contraseña actualizada correctamente.')
    return redirect('profile:view')
