from django.urls import path
from . import views

urlpatterns = [
    path('relation/', views.ir8, name='industrial_relation_dashboard'),
]