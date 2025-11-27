from django.urls import path
from . import views

urlpatterns = [
    path('test_form/<int:company_id>/', views.test_form, name='test_form'),
    path('personality_test/', views.big5_test_view, name='personality_test'),
    path('dope_test/', views.dope_test, name='dope_test'),
    path('thank_you/', views.thank_you, name='thank_you'),

    path('dashboard/', views.RecruitDashboardView.as_view(), name='recruit_dashboard'),
    path('generate_link/', views.generate_link, name='generate_link'),
    path('personality_test_result/', views.personality_test_result, name='personality_test_result'),
    path('dope_test_result/', views.dope_test_result, name='dope_test_result'),  # Route for a specific test
    path('pertanyaan_interviews/', views.PertanyaanInterviewView.as_view(), name='pertanyaan_interviews'),
    path('interviews/', views.interviews, name='interviews'),  #
]
