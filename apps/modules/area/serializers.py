from rest_framework import serializers

from apps.modules.area.models import Provinsi, KabupatenKota, Kecamatan, Desa


class ProvinsiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provinsi
        fields = ["id", "kode", "nama"]


class KabupatenKotaSerializer(serializers.ModelSerializer):
    provinsi_id = serializers.IntegerField(read_only=True)
    provinsi = ProvinsiSerializer(read_only=True)

    class Meta:
        model = KabupatenKota
        fields = ["id", "kode", "nama", "jenis", "provinsi_id", "provinsi"]


class KecamatanSerializer(serializers.ModelSerializer):
    kabupaten_kota_id = serializers.IntegerField(source="kabupaten_kota_id", read_only=True)
    kabupaten_kota = KabupatenKotaSerializer(read_only=True)

    class Meta:
        model = Kecamatan
        fields = ["id", "kode", "nama", "kabupaten_kota_id", "kabupaten_kota"]


class DesaSerializer(serializers.ModelSerializer):
    kecamatan_id = serializers.IntegerField(source="kecamatan_id", read_only=True)
    kecamatan = KecamatanSerializer(read_only=True)

    class Meta:
        model = Desa
        fields = [
            "id",
            "kode",
            "nama",
            "jenis",
            "kode_pos",
            "kecamatan_id",
            "kecamatan",
            "alamat_lengkap",
        ]
