from django.urls import path
from . import views

urlpatterns = [
    path('learning/', views.learning5, name='learning5_dashboard'),
]