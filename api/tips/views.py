from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .models import Tip, TipContributor, TipDiscussion
from .serializers import TipSerializer, TipContributorSerializer, TipDiscussionSerializer
from api.permission import HasValidAppKey

@api_view(['GET', 'POST'])
@permission_classes([HasValidAppKey])
def tips_list(request):
    if request.method == 'GET':
        tips = Tip.objects.all().order_by('-created_at')
        serializer = TipSerializer(tips, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Get user identifier from request headers
        user_identifier = getattr(request, 'user_identifier', None)
        if user_identifier:
            request.data['discussion'] = user_identifier
        
        serializer = TipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TipForm(forms.ModelForm):
    class Meta:
        model = Tip
        fields = ['title', 'content', 'category', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Judul menarik'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Tulis isi tip detail...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://... (opsional)'}),
        }


class TipContributorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'consultation/tip_contributor_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        self.contributor = getattr(request.user, 'tip_contributor_profile', None)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        if hasattr(self, '_form'):
            return self._form
        return TipForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.contributor:
            context['error_message'] = (
                'Akun Anda belum terdaftar sebagai kontributor tip. Hubungi admin untuk mendapatkan akses.'
            )
            context['tips'] = Tip.objects.none()
            context['form'] = None
            return context

        context.update({
            'contributor': self.contributor,
            'tips': self.contributor.tips.order_by('-created_at'),
            'form': self.get_form(),
        })
        return context

    def post(self, request, *args, **kwargs):
        if not self.contributor:
            messages.error(request, 'Akun Anda belum terdaftar sebagai kontributor tip.')
            return redirect(reverse('tips:tip_contributor_dashboard'))

        self._form = TipForm(request.POST)
        if self._form.is_valid():
            tip = self._form.save(commit=False)
            tip.contributor = self.contributor
            tip.save()
            messages.success(request, 'Tip baru berhasil dipublikasikan!')
            return redirect(reverse('tips:tip_contributor_dashboard'))

        messages.error(request, 'Periksa kembali formulir Anda.')
        return self.get(request, *args, **kwargs)

@api_view(['GET', 'POST'])
@permission_classes([HasValidAppKey])
def contributors_list(request):
    if request.method == 'GET':
        contributors = TipContributor.objects.all()
        serializer = TipContributorSerializer(contributors, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TipContributorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'POST'])
@permission_classes([HasValidAppKey])
def tip_discussions(request, tip_id):
    if request.method == 'GET':
        discussions = TipDiscussion.objects.filter(tip_id=tip_id)
        serializer = TipDiscussionSerializer(discussions, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Get user identifier from request headers
        user_identifier = getattr(request, 'user_identifier', None)
        
        # If no user_identifier, try to get it from headers directly
        if not user_identifier:
            email = request.headers.get('X-EMAIL')
            phone = request.headers.get('X-PHONE')
            
            if email and phone:
                user_identifier = f"{email}|{phone}"
            elif email:
                user_identifier = email
            elif phone:
                user_identifier = phone
            else:
                user_identifier = "unknown"
        
        # Create data with user_identifier
        discussion_data = {
            'tip': tip_id,
            'message': request.data.get('message', ''),
            'user_identifier': user_identifier
        }
        
        serializer = TipDiscussionSerializer(data=discussion_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

