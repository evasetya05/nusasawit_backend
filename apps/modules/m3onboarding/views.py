from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, FormView
from django.http import JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse, reverse_lazy
from apps.core.models import Employee
from apps.modules.m2recruit.models import TestResult
from .forms import EmployeeForm, EmployeeEditForm, SOPSuggestionForm
from .models import DocumentStandar

from .services.test_services import get_recruitment_tests


class DocumentView(LoginRequiredMixin, FormView):
    """
    View for handling document uploads and display.
    Only owners can upload documents.
    """
    template_name = 'm3onboarding/document.html'
    form_class = SOPSuggestionForm
    success_url = reverse_lazy('m3onboarding:sop')

    def get_context_data(self, **kwargs):
        """Add documents to the context."""
        context = super().get_context_data(**kwargs)
        context['docs'] = DocumentStandar.objects.all()
        return context

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        if not self.request.user.is_owner:
            messages.error(self.request, 'Hanya owner yang dapat mengunggah dokumen.')
            return redirect('m3onboarding:sop')

        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        messages.success(self.request, 'Dokumen berhasil diunggah.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """If the form is invalid, show an error message."""
        messages.error(self.request, 'Periksa kembali input Anda.')
        return super().form_invalid(form)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    context_object_name = 'employees'

    def get_queryset(self):
        return Employee.objects.filter(company=self.request.user.company)

    def get_template_names(self):
        if self.request.user.is_owner:
            return ['m3onboarding/struktur_organisasi/employee_list.html']
        return ['m3onboarding/struktur_organisasi/index.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EmployeeForm()
        candidates = TestResult.objects.filter(
            company=self.request.user.company,
            result=TestResult.ResultOptions.LULUS,
        ).select_related("user").order_by("user__name")
        context['candidate_options'] = [
            {
                "id": candidate.id,
                "name": candidate.user.name if candidate.user else "",
                "email": candidate.user.email if candidate.user else "",
            }
            for candidate in candidates
            if candidate.user
        ]
        return context

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_owner:
            return JsonResponse({
                'success': False,
                'errors': 'You are not allowed to add employee.'
            }, status=400)
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.company = request.user.company
            employee.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Employee added successfully.'
                })
            messages.success(request, 'Employee added successfully.')
            return redirect('company:employee-list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['form'] = form
            messages.error(request, 'Please correct the error below.')
            return self.render_to_response(context)


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'm3onboarding/struktur_organisasi/employee_detail.html'
    context_object_name = 'employee'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return Employee.objects.filter(company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recruitment_tests'] = get_recruitment_tests(self.object)
        context['employee_age'] = self.object.age
        return context


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeEditForm
    template_name = 'm3onboarding/struktur_organisasi/employee_edit.html'
    pk_url_kwarg = 'id'
    context_object_name = 'employee'
    permission_denied_message = "You don't have permission to update this employee's data."

    def get_queryset(self):
        return Employee.objects.filter(company=self.request.user.company)

    def dispatch(self, request, *args, **kwargs):
        # Get the employee object being updated
        self.object = self.get_object()

        # Allow access if user is the owner (checking company) or updating their own data
        if not (request.user.is_owner or request.user == self.object.user):
            messages.error(request, self.permission_denied_message)
            return redirect('m3onboarding:struktur_organisasi')

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def get_success_url(self):
        return reverse_lazy('m3onboarding:employee-detail', kwargs={'id': self.object.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Employee updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['recruitment_tests'] = get_recruitment_tests(self.object)
        context['employee_age'] = self.object.age
        return context


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'm3onboarding/struktur_organisasi/employee_confirm_delete.html'
    pk_url_kwarg = 'id'
    context_object_name = 'employee'
    success_message = 'Employee has been deleted successfully.'

    def get_queryset(self):
        return Employee.objects.filter(company=self.request.user.company)

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('m3onboarding:struktur_organisasi')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    @method_decorator(require_http_methods(["POST"]))
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
