from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('', views.profile_view, name='view'),
    path('update/', views.update_profile, name='update'),
    path('cancel-membership/', views.cancel_membership, name='cancel_membership'),
    path('change-password/', views.change_password, name='change_password'),
]
