from django.urls import path
from . import views

urlpatterns = [
        path('dope/', views.dope, name='dope'),
]
