from django.urls import path

from apps.modules.area import views

app_name = "area"

urlpatterns = [
    path("provinsi/", views.ProvinsiListView.as_view(), name="provinsi-list"),
    path("kabupaten-kota/", views.KabupatenKotaListView.as_view(), name="kabupaten-kota-list"),
    path("kecamatan/", views.KecamatanListView.as_view(), name="kecamatan-list"),
    path("desa/", views.DesaListView.as_view(), name="desa-list"),
]
