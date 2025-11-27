from django.urls import path
from . import views

app_name = 'm3onboarding'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sop/', views.sopView, name='sop'),

    path('struktur-organisasi/', views.EmployeeListView.as_view(), name='struktur_organisasi'),
    path('struktur-organisasi/<int:id>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('struktur-organisasi/<int:id>/edit/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('struktur-organisasi/<int:id>/delete/', views.EmployeeDeleteView.as_view(), name='employee-delete'),

    path('saran-perusahaan/', views.saranPerusahaanView, name='saran_perusahaan'),
    path('rencana-training/', views.rencanaTrainingView, name='rencana_training'),
]
