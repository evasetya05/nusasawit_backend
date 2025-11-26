from django.urls import path
from apps.tips.views import tips_list

app_name = 'tips'

urlpatterns = [
    path('', tips_list, name='tips_list'),
]