from django.urls import path
from . import views

app_name = 'm9improvement'
urlpatterns = [
    path('dashboard/', views.continues_improvement_dashboard, name='dashboard'),
    path('ocai/', views.ocai_form, name='ocai_form'),
    path('result_ocai/', views.result_ocai, name='result_ocai'),
    path('thank_you/', views.thankyou, name='thank_you'),
]
