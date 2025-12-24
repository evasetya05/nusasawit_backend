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



    
    path('m1planning/', include('apps.modules.m1planning.urls'), name="planning"),
  
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
    path('area/', include('apps.modules.area.urls'), name="area"),
    path('inbox/', include('apps.modules.inbox.urls'), name="inbox"),


    path('psychometric/', include('apps.extras.psychometric.urls'),
         name="psychometric"),
    path('blog/', include('apps.extras.blog.urls')),  # Tambahkan ini
    path('', include('apps.extras.syarat_ketentuan.urls'), name="syarat_ketentuan"),

    path('api/tips/', include('api.tips.urls')),
    path('api/mitra/', include('api.mitra_borongan.urls')),
    path('api/consultation/', include('api.consultation.urls')),
    path('api/sertifikasi/', include('api.sertifikasi.urls')),
    path('api/pasar/', include('api.pasar.urls')),
    path('api/petunjuk/', include('api.petunjuk.urls')),
    path('peta/', include('api.waypoint.urls')),
    path('pasar/', include(('api.pasar.urls', 'pasar'), namespace='pasar_web')),
    

    path('ckeditor/', include('ckeditor_uploader.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [
    *urlpatterns,
] + debug_toolbar_urls()
