"""HRManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path("accounts/", include("apps.account.urls"), name='accounts'),
    path('', include('apps.core.urls')),
    path('', include('apps.extras.legal.urls'), name="legal"),
    path('jobs/', include('apps.extras.job.urls'), name="jobs"),
    path('vacancy/', include('apps.extras.vacancy.urls'), name="vacancy"),



    path('planing/', include('apps.modules.planing1.urls'), name="planing"),
    path('recruit/', include('apps.modules.m2recruit.urls'), name="recruit"),
    path('onboarding/', include('apps.modules.m3onboarding.urls'), name="onboarding"),
    path('kinerja/', include('apps.modules.kinerja4.urls'), name="kinerja"),
    path('learning/', include('apps.modules.learning5.urls'), name="learning"),
    path('compensation/', include('apps.modules.compensation6.urls'),
         name="compensation"),
    path('compliance/', include('apps.modules.compliance7.urls'), name="compliance"),
    path('industrial/', include('apps.modules.ir8.urls'), name="industrial"),
    path('continues_improvement/', include('apps.modules.m9improvement.urls'),
         name="continues_improvement"),


    path('psychometric/', include('apps.extras.psychometric.urls'),
         name="psychometric"),
    path('blog/', include('apps.extras.blog.urls')),  # Tambahkan ini

    path('api/tips/', include('tips.urls')),
    

    path('ckeditor/', include('ckeditor_uploader.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [
    *urlpatterns,
] + debug_toolbar_urls()
