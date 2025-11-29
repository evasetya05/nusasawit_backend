from django.urls import path
from .views import tips_list, contributors_list, tip_discussions
from . import views

app_name = 'tips'

urlpatterns = [
    path('', tips_list, name='tips_list'),
    path('contributors/', contributors_list, name='contributors_list'),
    path('<int:tip_id>/discussions/', tip_discussions, name='tip_discussions'),
]