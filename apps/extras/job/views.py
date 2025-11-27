from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, ListView, UpdateView
from .models import Jobs
from .forms import JobForm


# Create your views here.
class JobCreateView(FormView):
    success_url = reverse_lazy('dashboard:index')
    template_name = 'Job/add-job.html'
    form_class = JobForm

    def form_valid(self, form):
        current_form = form.save(commit=False)
        team_lead = form.cleaned_data['team_lead']
        print(team_lead.id)
        if team_lead.user_position != 'TL':
            form.add_error("team_lead", "The team lead must be registered as a Team lead")
            return super().form_invalid(form)

        form.save(commit=True)

        return super().form_valid(form)


class JobUpdateView(UpdateView):
    template_name = "Job/edit-job.html"
    success_url = reverse_lazy('dashboard:index')
    form_class = JobForm
    queryset = Jobs.objects.all()


class JobDeleteView(DeleteView):
    model = Jobs
    success_url = reverse_lazy('dashboard:index')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
