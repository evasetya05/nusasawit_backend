from django.urls import path

from .views import waypoint_deep_link

app_name = "waypoint"

urlpatterns = [
    path("", waypoint_deep_link, name="deep_link"),
]
