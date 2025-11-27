from django.urls import path
from . import views

app_name = 'm3onboarding'
urlpatterns = [
    path('document/', views.DocumentView.as_view(), name='document'),

    path('struktur-organisasi/', views.EmployeeListView.as_view(), name='struktur_organisasi'),
    path('struktur-organisasi/<int:id>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('struktur-organisasi/<int:id>/edit/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('struktur-organisasi/<int:id>/delete/', views.EmployeeDeleteView.as_view(), name='employee-delete'),
]
