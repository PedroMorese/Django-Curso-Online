from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps

@login_required
def profile_view(request):
    # Intentar obtener la membresía activa del usuario
    UserMembership = apps.get_model('membership', 'UserMembership')
    membership = UserMembership.objects.filter(user=request.user, status='ACTIVE').first()
    
    # Determinar template base según rol
    if request.user.role == 'ADMIN':
        base_template = 'dashboard_admin/base_admin.html'
    elif request.user.role == 'PROFESOR':
        base_template = 'dashboard_profesor/base_profesor.html'
    else:
        # Clientes y otros roles usan la base del Home
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
        
        # Guardar cambios básicos
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
