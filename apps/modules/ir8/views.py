from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden

from .models import Complaint
from .forms import ComplaintCreateForm, ComplaintReviewForm


def ir8(request):
    return render(request, 'ir8/industrial_relation_dashboard.html')


@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintCreateForm(request.POST, request.FILES)
        user = request.user
        if form.is_valid():
            comp = form.save(commit=False)
            employee = user.person
            if not employee:
                messages.error(
                    request, "Profil Employee tidak ditemukan. Hubungi admin.")
                return redirect('ir8:complaint_list')
            comp.reporter = employee
            comp.company = user.company
            comp.status = 'submitted'
            comp.save()
            try:
                send_mail(
                    subject=f"Keluhan Baru: {comp.title}",
                    message=f"Ada keluhan baru dari {comp.reporter}. Lihat: {request.build_absolute_uri(reverse('ir8:complaint_detail', args=[comp.pk]))}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.company.owner.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "Keluhan berhasil dikirim.")
            return redirect('ir8:complaint_list')
    else:
        form = ComplaintCreateForm()
    return render(request, 'ir8/complaint_create.html', {'form': form})


class ComplaintListView(LoginRequiredMixin, ListView):
    model = Complaint
    template_name = 'ir8/complaint_list.html'
    context_object_name = 'complaints'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'POST' and request.user.is_authenticated and not request.user.is_owner:
            company = getattr(request.user, 'company', None)
            if company and not getattr(company, 'ir_menu_visible', True):
                return HttpResponseForbidden("Menu Industrial Relation sedang dinonaktifkan oleh owner.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_owner:
            return Complaint.objects.all()
        elif user.is_authenticated:
            employee = get_employee_for_user(user)
            company = getattr(user, 'company', None)
            if company and not getattr(company, 'ir_menu_visible', True):
                return Complaint.objects.none()
            if employee:
                return Complaint.objects.filter(reporter=employee)
            return Complaint.objects.none()
        else:
            return Complaint.objects.none()

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_owner:
            return HttpResponseForbidden()
        company = getattr(request.user, 'company', None)
        if not company:
            messages.error(request, "Perusahaan tidak ditemukan untuk akun Anda.")
            return redirect('ir8:complaint_list')

        desired_state = request.POST.get('set_ir_menu_visibility')
        if desired_state not in {'true', 'false'}:
            messages.error(request, "Permintaan tidak valid.")
            return redirect('ir8:complaint_list')

        company.ir_menu_visible = desired_state == 'true'
        company.save(update_fields=['ir_menu_visible'])

        if company.ir_menu_visible:
            messages.success(request, "Menu Industrial Relation kini terlihat oleh karyawan.")
        else:
            messages.success(request, "Menu Industrial Relation kini disembunyikan dari karyawan.")

        return redirect('ir8:complaint_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.request.user.is_owner
        company = getattr(self.request.user, 'company', None)
        context['company_ir_menu_visible'] = getattr(company, 'ir_menu_visible', True)
        return context

class ComplaintDetailView(DetailView):
    model = Complaint
    template_name = 'ir8/complaint_detail.html'


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_owner)
def review_complaint(request, pk):
    comp = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = ComplaintReviewForm(request.POST, instance=comp)
        if form.is_valid():
            comp = form.save(commit=False)
            reviewer_emp = request.user.person
            # reviewer bisa juga null jika tidak ada Employee profile untuk user staff
            if reviewer_emp:
                comp.reviewed_by = reviewer_emp
            if comp.status == 'resolved':
                comp.resolved_at = timezone.now()
            comp.save()
            # optional: send notification to reporter
            try:
                if comp.reporter and getattr(comp.reporter, 'email', None):
                    send_mail(
                        subject=f"Status Keluhan Anda: {comp.title}",
                        message=f"Status keluhan Anda sekarang: {comp.get_status_display()}.\nCatatan: {comp.review_notes or '-'}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[comp.reporter.email],
                        fail_silently=True,
                    )
            except Exception:
                pass
            messages.success(request, "Keluhan diperbarui.")
            return redirect(reverse('ir8:complaint_detail', args=[comp.pk]))
    else:
        form = ComplaintReviewForm(instance=comp)
    return render(request, 'ir8/complaint_review.html', {'form': form, 'complaint': comp})
