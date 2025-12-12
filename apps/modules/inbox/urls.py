from django.urls import path

from .views import InboxView

app_name = "inbox"

urlpatterns = [
    path("", InboxView.as_view(), name="thread_list"),
]
