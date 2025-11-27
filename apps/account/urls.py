from django.urls import include, path
from .views import (
    CustomRegistrationView, SendInvitationView, AcceptInvitationView
)

urlpatterns = [
    path('register/', CustomRegistrationView.as_view(), name="django_registration_register"),
    path("", include("django_registration.backends.activation.urls")),
    path('', include("django.contrib.auth.urls")),
    # path('invite/<uuid:token>', InviteView.as_view(), name="invite-staff"),

    # Employee and Invitation URLs
    path('employees/invite/<int:employee_id>/', SendInvitationView.as_view(), name='send-invitation'),
    path('invitation/accept/<uuid:token>/', AcceptInvitationView.as_view(), name='accept-invitation'),
]
