"""
URL configuration for djangocrud project.

Organizado en:
- Backend Domain URLs (API/lógica de negocio)
- Frontend UX URLs (experiencia de usuario)
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # ===========================================
    # BACKEND - Domain/API URLs (funcional)
    # ===========================================
    path('auth/', include('Back-end.Auth.urls')),
    path('api/courses/', include('Back-end.Course.urls')),
    path('api/classes/', include('Back-end.Class.urls')),
    path('api/membership/', include('Back-end.membership.urls')),
    
    # ===========================================
    # FRONTEND - Dashboard URLs
    # ===========================================
    path('dashboard/profesor/', include('Front-end.Dashboard-Profesor.MyCourses.urls')),
    path('dashboard/admin/', include('Front-end.Dashboard-Admin.Overview.urls')),
    
    # ===========================================
    # FRONTEND - UX URLs (Home)
    # La home se encarga de todas las rutas UX públicas
    # ===========================================
    path('', include('Front-end.home.urls')),
]
