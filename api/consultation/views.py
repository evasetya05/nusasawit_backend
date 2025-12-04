from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions

from .models import Consultant, Consultation, ConsultationMessage
from api.permission import HasValidAppKey
from api.user_flutter.models import FlutterUser
from .serializers import (
    ConsultantSerializer,
    ConsultationSerializer,
    ConsultationMessageSerializer,
    ConsultationListSerializer
)

class ConsultantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing consultants.
    """
    queryset = Consultant.objects.all()
    serializer_class = ConsultantSerializer
    permission_classes = [HasValidAppKey]


class ConsultationViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing consultations.
    """
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [HasValidAppKey]

    def get_queryset(self):
        """
        Filter konsultasi berdasarkan pengguna (petani) yang diidentifikasi
        melalui header X-EMAIL.
        """
        email = self.request.headers.get('X-EMAIL')
        if email:
            farmer = FlutterUser.objects.filter(email=email).first()
            if farmer:
                return Consultation.objects.filter(farmer=farmer)
        return Consultation.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultationListSerializer
        return ConsultationSerializer

    def perform_create(self, serializer):
        email = self.request.headers.get('X-EMAIL')
        phone = self.request.headers.get('X-PHONE')

        # Dapatkan pengguna Flutter pertama yang cocok dengan email, atau buat yang baru jika tidak ada.
        # Ini mencegah error 'MultipleObjectsReturned'.
        farmer = FlutterUser.objects.filter(email=email).first()
        if not farmer:
            farmer = FlutterUser.objects.create(
                email=email,
                defaults={'phone': phone, 'identifier': email}
            )

        serializer.save(farmer=farmer)


class ConsultationMessageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and creating consultation messages within a consultation.
    """
    queryset = ConsultationMessage.objects.all()
    serializer_class = ConsultationMessageSerializer
    permission_classes = [HasValidAppKey]

    def get_queryset(self):
        """
        Filter messages to only those belonging to the specified consultation,
        and ensure the requestor owns the consultation.
        """
        email = self.request.headers.get('X-EMAIL')
        consultation_pk = self.kwargs.get('consultation_pk')

        if email:
            farmer = FlutterUser.objects.filter(email=email).first()
            if farmer:
                # Filter pesan yang konsultasinya dimiliki oleh farmer yang melakukan request
                return self.queryset.filter(consultation_id=consultation_pk, consultation__farmer=farmer)
        return self.queryset.none()

    def perform_create(self, serializer):
        """
        Associate the message with the correct consultation from the URL
        and the sender from the request headers.
        """
        consultation = Consultation.objects.get(pk=self.kwargs['consultation_pk'])
        email = self.request.headers.get('X-EMAIL')
        farmer = FlutterUser.objects.filter(email=email).first()

        # Set sender based on who is making the request
        serializer.save(consultation=consultation, sender_farmer=farmer)


class ConsultantDashboardView(LoginRequiredMixin, TemplateView):
    """Simple web dashboard for consultants to respond to consultations."""

    template_name = 'consultation/consultant_dashboard.html'

    def get_consultant(self):
        return getattr(self.request.user, 'consultant_profile', None)

    def get_selected_consultation(self, consultant, consultations):
        selected_id = self.request.GET.get('consultation')
        if selected_id:
            return consultations.filter(pk=selected_id).first()
        return consultations.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultant = self.get_consultant()

        if not consultant:
            context['error_message'] = (
                'Akun Anda belum terhubung sebagai konsultan. Mohon hubungi administrator.'
            )
            context['consultations'] = Consultation.objects.none()
            context['active_consultation'] = None
            context['messages'] = ConsultationMessage.objects.none()
            return context

        consultations = (
            consultant.consultations.select_related('farmer')
            .prefetch_related('messages')
            .order_by('-created_at')
        )
        active_consultation = self.get_selected_consultation(consultant, consultations)

        if active_consultation:
            messages_qs = (
                ConsultationMessage.objects.filter(consultation=active_consultation)
                .select_related('sender_farmer', 'sender_consultant')
                .order_by('created_at')
            )
        else:
            messages_qs = ConsultationMessage.objects.none()

        context.update({
            'consultant': consultant,
            'consultations': consultations,
            'active_consultation': active_consultation,
            'messages': messages_qs,
        })
        return context

    def post(self, request, *args, **kwargs):
        consultant = self.get_consultant()
        if not consultant:
            messages.error(request, 'Akun Anda belum terhubung sebagai konsultan.')
            return redirect('consultation:consultant_dashboard')

        consultation_id = request.POST.get('consultation_id')
        content = (request.POST.get('content') or '').strip()
        image = request.FILES.get('image')

        if not consultation_id:
            messages.error(request, 'Konsultasi tidak ditemukan.')
            return redirect('consultation:consultant_dashboard')

        consultation = get_object_or_404(
            Consultation, pk=consultation_id, consultant=consultant
        )

        if not content and not image:
            messages.error(request, 'Isi pesan atau lampirkan gambar sebelum mengirim.')
            return redirect(f"{reverse('consultation:consultant_dashboard')}?consultation={consultation.id}")

        ConsultationMessage.objects.create(
            consultation=consultation,
            sender_consultant=consultant,
            content=content or None,
            image=image,
        )
        messages.success(request, 'Pesan berhasil dikirim.')
        return redirect(f"{reverse('consultation:consultant_dashboard')}?consultation={consultation.id}")