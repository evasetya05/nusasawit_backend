from django.urls import path
from . import views

urlpatterns = [
    path('perencanaan/', views.planing1, name='planing1_dashboard'),
]