from django.urls import path
from . import views

app_name = 'ir8'

urlpatterns = [
    path('', views.ComplaintListView.as_view(), name='complaint_list'),
    path('complaints/', views.ComplaintListView.as_view(), name='complaint_list'),
    path('complaints/create/', views.create_complaint, name='complaint_create'),
    path('complaints/<int:pk>/', views.ComplaintDetailView.as_view(), name='complaint_detail'),
    path('complaints/<int:pk>/review/', views.review_complaint, name='complaint_review'),
]
