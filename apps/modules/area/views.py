from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ValidationError

from api.permission import HasValidAppKey
from apps.modules.area.models import Provinsi, KabupatenKota, Kecamatan, Desa
from apps.modules.area.serializers import (
    ProvinsiSerializer,
    KabupatenKotaSerializer,
    KecamatanSerializer,
    DesaSerializer,
)


class ProvinsiListView(ListAPIView):
    """Daftar provinsi untuk kebutuhan master data frontend."""

    permission_classes = [HasValidAppKey]
    serializer_class = ProvinsiSerializer
    queryset = Provinsi.objects.all().order_by("nama")


class KabupatenKotaListView(ListAPIView):
    """Daftar kabupaten/kota, bisa difilter berdasarkan provinsi."""

    permission_classes = [HasValidAppKey]
    serializer_class = KabupatenKotaSerializer

    def get_queryset(self):
        queryset = (
            KabupatenKota.objects.select_related("provinsi")
            .all()
            .order_by("nama")
        )
        provinsi_id = self.request.query_params.get("provinsi_id")
        if provinsi_id:
            try:
                provinsi_id_int = int(provinsi_id)
            except (TypeError, ValueError):
                raise ValidationError({"provinsi_id": "Harus berupa angka."})
            queryset = queryset.filter(provinsi_id=provinsi_id_int)
        return queryset


class KecamatanListView(ListAPIView):
    """Daftar kecamatan, bisa difilter berdasarkan kabupaten/kota."""

    permission_classes = [HasValidAppKey]
    serializer_class = KecamatanSerializer

    def get_queryset(self):
        queryset = (
            Kecamatan.objects.select_related("kabupaten_kota", "kabupaten_kota__provinsi")
            .all()
            .order_by("nama")
        )
        kabupaten_kota_id = self.request.query_params.get("kabupaten_kota_id")
        if kabupaten_kota_id:
            try:
                kabupaten_kota_id_int = int(kabupaten_kota_id)
            except (TypeError, ValueError):
                raise ValidationError({"kabupaten_kota_id": "Harus berupa angka."})
            queryset = queryset.filter(kabupaten_kota_id=kabupaten_kota_id_int)
        return queryset


class DesaListView(ListAPIView):
    """Daftar desa/kelurahan, bisa difilter berdasarkan kecamatan."""

    permission_classes = [HasValidAppKey]
    serializer_class = DesaSerializer

    def get_queryset(self):
        queryset = (
            Desa.objects.select_related(
                "kecamatan",
                "kecamatan__kabupaten_kota",
                "kecamatan__kabupaten_kota__provinsi",
            )
            .all()
            .order_by("nama")
        )
        kecamatan_id = self.request.query_params.get("kecamatan_id")
        if kecamatan_id:
            try:
                kecamatan_id_int = int(kecamatan_id)
            except (TypeError, ValueError):
                raise ValidationError({"kecamatan_id": "Harus berupa angka."})
            queryset = queryset.filter(kecamatan_id=kecamatan_id_int)
        return queryset
