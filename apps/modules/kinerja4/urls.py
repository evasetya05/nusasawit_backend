from django.urls import path
from . import views

urlpatterns = [
    path('kinerja/', views.kinerja4, name='kinerja4_dashboard'),
]