from django.urls import path
from . import views

urlpatterns = [
    path('compensation/', views.compensation6, name='compensation6_dashboard'),
]