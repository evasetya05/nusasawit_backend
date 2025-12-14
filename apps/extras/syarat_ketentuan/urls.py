from django.urls import path
from . import views

app_name = 'syarat_ketentuan'

urlpatterns = [
    # Public URLs (accessible by anyone)
    path('syarat-dan-ketentuan/', views.syarat_dan_ketentuan_public, name='syarat_dan_ketentuan_public'),
    path('kebijakan-privasi/', views.kebijakan_privasi_public, name='kebijakan_privasi_public'),
    
    # Admin URLs (protected)
    path('admin/create/', views.create_syarat_ketentuan, name='create_syarat_ketentuan'),
    path('admin/', views.syarat_ketentuan_list, name='syarat_ketentuan_list'),
    path('admin/<slug:slug>/', views.syarat_ketentuan_detail, name='syarat_ketentuan_detail'),
]

