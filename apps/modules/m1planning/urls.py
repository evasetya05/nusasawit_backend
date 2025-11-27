"""URL configuration for the M1 Planning module."""
from django.urls import path

from . import views

app_name = 'm1planning'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # LCR Records
    path('lcr/', views.LCRRecordListView.as_view(), name='list'),
    path('lcr/new/', views.LCRRecordCreateView.as_view(), name='create'),
    path('lcr/<int:pk>/', views.LCRRecordUpdateView.as_view(), name='update'),
    path('lcr/<int:pk>/delete/', views.LCRRecordDeleteView.as_view(), name='delete'),

]
