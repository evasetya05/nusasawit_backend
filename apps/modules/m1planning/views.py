"""Views for the M1 Planning module."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)

from .models import LCRRecord
from .forms import LCRRecordForm


class LCRRecordListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View for listing LCR records."""
    model = LCRRecord
    template_name = "m1planning/lcr_list.html"
    context_object_name = "records"
    paginate_by = 10
    permission_denied_message = _(
        "You don't have permission to view LCR records."
    )

    def test_func(self):
        """Check if user has view permission."""
        return self.request.user.has_perm("m1planning.view_lcrrecord")

    def handle_no_permission(self):
        """Handle unauthorized access."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, self.permission_denied_message)
        return redirect(reverse("dashboard"))

    def get_queryset(self):
        """Filter records by the user's company."""
        qs = super().get_queryset()
        return qs.filter(company=self.request.user.company)

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = _("Labor Cost Ratio Records")
        return context


class LCRRecordCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for creating a new LCR record."""
    model = LCRRecord
    form_class = LCRRecordForm
    template_name = "m1planning/lcr_form.html"
    permission_denied_message = _(
        "You don't have permission to add LCR records."
    )

    def test_func(self):
        """Check if user has add permission."""
        return self.request.user.has_perm("m1planning.add_lcrrecord")

    def handle_no_permission(self):
        """Handle unauthorized access."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, self.permission_denied_message)
        return redirect(reverse("m1planning:list"))

    def get_form_kwargs(self):
        """Add company to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        """Set the company and handle successful form submission."""
        form.instance.company = self.request.user.company
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("LCR record has been created successfully.")
        )
        return response

    def get_success_url(self):
        """Redirect to the list view after successful creation."""
        return reverse("m1planning:list")

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = _("Add New LCR Record")
        context["submit_text"] = _("Create Record")
        return context


class LCRRecordUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing LCR record."""
    model = LCRRecord
    form_class = LCRRecordForm
    template_name = "m1planning/lcr_form.html"
    permission_denied_message = _(
        "You don't have permission to change LCR records."
    )

    def test_func(self):
        """Check if user has change permission for this record."""
        if not self.request.user.has_perm("m1planning.change_lcrrecord"):
            return False
        # Additional check: user can only update records for their own company
        obj = self.get_object()
        return obj.company == self.request.user.company

    def handle_no_permission(self):
        """Handle unauthorized access."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, self.permission_denied_message)
        return redirect(reverse("m1planning:list"))

    def get_form_kwargs(self):
        """Add company to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("LCR record has been updated successfully.")
        )
        return response

    def get_success_url(self):
        """Redirect to the list view after successful update."""
        return reverse("m1planning:list")

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context["title"] = _("Update LCR Record")
        context["submit_text"] = _("Update Record")
        return context


class LCRRecordDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting an LCR record."""
    model = LCRRecord
    template_name = "m1planning/lcr_confirm_delete.html"
    success_url = reverse_lazy("m1planning:list")
    permission_denied_message = _(
        "You don't have permission to delete LCR records."
    )

    def test_func(self):
        """Check if user has delete permission for this record."""
        if not self.request.user.has_perm("m1planning.delete_lcrrecord"):
            return False
        # Additional check: user can only delete records for their own company
        obj = self.get_object()
        return obj.company == self.request.user.company

    def handle_no_permission(self):
        """Handle unauthorized access."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, self.permission_denied_message)
        return redirect(reverse("m1planning:list"))

    def delete(self, request, *args, **kwargs):
        """Handle successful deletion."""
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            _("LCR record has been deleted successfully.")
        )
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the M1 Planning module."""
    template_name = "m1planning/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get user's company
        user_company = self.request.user.company

        # Get all LCR records for the user's company
        records = LCRRecord.objects.filter(company=user_company)

        # Calculate statistics
        total_records = records.count()

        # Calculate average LCR properly
        avg_lcr = None
        if records.exists() and records.filter(total_income__gt=0).exists():
            avg_lcr_result = records.filter(total_income__gt=0).aggregate(
                avg_lcr=Avg('total_labor_cost') * 100.0 / Avg('total_income')
            )
            avg_lcr = avg_lcr_result['avg_lcr']

        # Get latest record
        latest_record = records.order_by('-period').first()

        # Get recent records (last 5)
        recent_records = records.order_by('-created_at')[:5]

        context.update({
            'total_records': total_records,
            'avg_lcr': avg_lcr,
            'latest_record': latest_record,
            'recent_records': recent_records,
        })

        return context
