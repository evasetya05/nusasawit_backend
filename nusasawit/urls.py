from django.contrib import admin
from django.urls import path, include
from apps.tips import views as tips_views  # <--- HARUS ADA

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tips/', include('apps.tips.urls')),
    path('test-log/', tips_views.test_log),  # sekarang tips_views dikenali
]
