from django.urls import path
from . import views

app_name = 'media_backend'

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
]
