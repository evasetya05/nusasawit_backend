# apps/learning5/urls.py
from django.urls import path
from . import views

app_name = 'learning5'

urlpatterns = [
    path('', views.learning_dashboard, name='dashboard'),
    path('trainingneed/', views.trainingneed_list, name='trainingneed_list'),
    path('trainingneed/add/', views.trainingneed_add, name='trainingneed_add'),
    path('trainingneed/<int:pk>/edit/', views.trainingneed_edit, name='trainingneed_edit'),
    path('trainingneed/<int:pk>/delete/', views.trainingneed_delete, name='trainingneed_delete'),
    path('competency/add/', views.competency_add, name='competency_add'),
    path('competency/<int:pk>/edit/', views.competency_add, name='competency_edit'),
    path('ajax/load-detail-competencies/', views.load_detail_competencies, name='ajax_load_detail_competencies'),
]
