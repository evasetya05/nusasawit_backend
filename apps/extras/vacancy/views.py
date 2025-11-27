from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.conf import settings

from .forms import ApplicationForm
from apps.extras.job.models import Jobs, Application


@method_decorator(login_required, name='dispatch')
class ApplyJobView(FormView):
    form_class = ApplicationForm
    template_name = 'Vacency/apply_job.html'
    success_url = reverse_lazy('dashboard:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs.get('pk')
        job = Jobs.objects.get(id=job_id)
        # print(job)
        context['job'] = job.title
        return context

    def form_valid(self, form):
        job_id = self.kwargs.get('pk')
        job = Jobs.objects.get(id=job_id)
        applicant = self.request.user

        self.object = form.save(commit=False)
        self.object.job = job
        self.object.applicant = applicant
        self.object.save()

        return super(ApplyJobView, self).form_valid(form)

    def form_invalid(self, form):
        print('form is invalid')
        return super(ApplyJobView, self).form_invalid(form)


def select_for_exam(request, application_id):

    #send mail
    current_site = get_current_site(request)
    current_application = Application.objects.get(id=application_id)
    subject = 'Activate Your Asmit Blogs Account'
    message = f"You have been selected for the Online interview! " \
              f"Take exam {current_site}/exam/{current_application.job.id}"
    print(current_application.applicant.email)
    send_mail(subject, message, EMAIL_HOST_USER, [current_application.applicant.email], fail_silently=False)

    current_application.selected_for_exam = True
    current_application.save()

    return redirect('dashboard:index')


def cancel_for_exam(request, application_id):

    #send mail
    current_site = get_current_site(request)
    current_application = Application.objects.get(id=application_id)
    subject = 'Activate Your Asmit Blogs Account'
    message = f"You have not been selected for the Online interview! " \
              f"Take exam {current_site}/exam/{current_application.job.id}"
    print(current_application.applicant.email)
    send_mail(subject, message, EMAIL_HOST_USER, [current_application.applicant.email], fail_silently=False)

    current_application.canceled_for_exam = True
    current_application.save()

    return redirect('dashboard:index')


def view_cv(request, application_id):
    current_application = Application.objects.get(id=application_id)
