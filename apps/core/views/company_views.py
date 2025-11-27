from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..models import Company, Department, Position


class UpdateCompanyView(LoginRequiredMixin, UpdateView):
    model = Company
    fields = ['name', 'address', 'phone', 'email', 'website', 'logo']
    template_name = 'company/update-company.html'
    success_url = reverse_lazy('company:profile')

    def get_object(self):
        user = self.request.user
        if user.is_owner():
            return user.company
        raise Http404()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Company profile updated successfully.')
        return response


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'company/department_list.html'
    context_object_name = 'departments'

    def get_queryset(self):
        if self.request.user.is_owner():
            return Department.objects.filter(company=self.request.user.company)
        raise Http404()


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    fields = ['name']
    template_name = 'company/department_form.html'

    def form_valid(self, form):
        if not self.request.user.is_owner():
            raise Http404()
        form.instance.company = self.request.user.company
        messages.success(self.request, 'Department created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('company:department')


class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Department
    fields = ['name']
    template_name = 'company/department_form.html'
    context_object_name = 'department'

    def get_queryset(self):
        if self.request.user.is_owner():
            return Department.objects.filter(company=self.request.user.company)
        raise Http404()

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('company:department')


class DepartmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Department
    template_name = 'company/department_confirm_delete.html'
    context_object_name = 'department'

    def get_queryset(self):
        if self.request.user.is_owner():
            return Department.objects.filter(company=self.request.user.company)
        raise Http404()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Department deleted successfully.')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('company:department')


class PositionListView(LoginRequiredMixin, ListView):
    model = Position
    template_name = 'company/position_list.html'
    context_object_name = 'positions'

    def get_queryset(self):
        if self.request.user.is_owner():
            return Position.objects.filter(department__company=self.request.user.company)
        raise Http404()


class PositionCreateView(LoginRequiredMixin, CreateView):
    model = Position
    fields = ['name', 'department']
    template_name = 'company/position_form.html'

    def form_valid(self, form):
        if not self.request.user.is_owner():
            raise Http404()
        form.instance.company = self.request.user.company
        messages.success(self.request, 'Position created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('company:position')


class PositionUpdateView(LoginRequiredMixin, UpdateView):
    model = Position
    fields = ['name', 'department']
    template_name = 'company/position_form.html'
    context_object_name = 'position'

    def get_queryset(self):
        if self.request.user.is_owner():
            return Position.objects.filter(department__company=self.request.user.company)
        raise Http404()

    def form_valid(self, form):
        messages.success(self.request, 'Position updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('company:position')


class PositionDeleteView(LoginRequiredMixin, DeleteView):
    model = Position
    template_name = 'company/position_confirm_delete.html'
    context_object_name = 'position'

    def get_queryset(self):
        if self.request.user.is_owner():
            return Position.objects.filter(department__company=self.request.user.company)
        raise Http404()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Position deleted successfully.')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('company:position')
