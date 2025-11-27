import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth import login
from django_registration.backends.activation.views import RegistrationView

from .models import Invitation
from .forms import UserRegistrationForm, AcceptInvitationForm

from apps.core.models import Employee


class CustomRegistrationView(RegistrationView):
    form_class = UserRegistrationForm


class SendInvitationView(LoginRequiredMixin, View):
    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)

        # Security check: ensure the request user is the owner of the company
        if not request.user.is_owner or employee.company != request.user.company:
            messages.error(
                request, "You don't have permission to perform this action.")
            return redirect(request.META.get('HTTP_REFERER'))

        # Update invitation details
        invitation, created = Invitation.objects.update_or_create(
            email=employee.email,
            company=employee.company,
            defaults={
                'created_by': request.user,
                'token': uuid.uuid4(),
                'expires_at': timezone.now() + timezone.timedelta(days=7),
                'status': Invitation.Status.PENDING
            }
        )

        # Send email
        current_site = get_current_site(request)
        accept_url = reverse('accept-invitation',
                             kwargs={'token': invitation.token})
        subject = 'You are invited to join our platform'
        message = render_to_string('account/invitation_email.html', {
            'user': employee,
            'domain': current_site.domain,
            'accept_url': request.build_absolute_uri(accept_url),
        })
        send_mail(subject, message, settings.EMAIL_HOST_USER, [employee.email])

        messages.success(request, f'Invitation sent to {employee.email}.')
        return redirect(request.META.get('HTTP_REFERER'))


class AcceptInvitationView(View):
    def get(self, request, token):
        try:
            invitation = Invitation.objects.get(token=token)
            employee = Employee.objects.get(email=invitation.email)
        except Invitation.DoesNotExist or Employee.DoesNotExist:
            messages.error(request, 'Invalid invitation link.')
            return redirect('login')  # Or a custom invalid token page

        # Check if token is expired
        if timezone.now() > invitation.expires_at:
            messages.error(request, 'This invitation link has expired.')
            invitation.status = Invitation.Status.EXPIRED
            invitation.save()
            return redirect('login')

        form = AcceptInvitationForm()
        return render(request, 'account/accept_invitation.html', {'form': form, 'user': employee})

    def post(self, request, token):
        try:
            invitation = Invitation.objects.get(token=token)
            employee = Employee.objects.get(email=invitation.email)
        except Invitation.DoesNotExist or Employee.DoesNotExist:
            messages.error(request, 'Invalid invitation link.')
            return redirect('login')

        form = AcceptInvitationForm(request.POST)
        if form.is_valid():
            # Set password and activate user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.email = employee.email
            user.invitation = invitation
            user.company = employee.company
            user.save()
            employee.user = user
            employee.save()
            invitation.status = Invitation.Status.ACCEPTED
            invitation.save()

            # Log the user in
            login(request, user)
            return redirect('dashboard')

        return render(request, 'account/accept_invitation.html', {'form': form, 'user': employee})
