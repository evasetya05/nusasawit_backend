from django.urls import path
from . import views

urlpatterns = [
    path('compliance/', views.compliance7, name='compliance_dashboard'),
]