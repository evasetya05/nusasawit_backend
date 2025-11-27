from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('create/', views.create_blog, name='create_blog'),
    path('', views.blog_list, name='blog_list'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),  # URL berbasis slug
]

