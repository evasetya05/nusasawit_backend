from django.urls import path
from apps.tips.views import tips_list
from . import views

app_name = 'tips'

urlpatterns = [
    path('', tips_list, name='tips_list'),

    path('test-log/', views.test_log),
]