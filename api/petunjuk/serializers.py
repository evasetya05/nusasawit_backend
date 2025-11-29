from rest_framework import serializers
from .models import Petunjuk, PetunjukKategori, PetunjukBaca


class PetunjukKategoriSerializer(serializers.ModelSerializer):
    """Serializer untuk kategori petunjuk"""
    class Meta:
        model = PetunjukKategori
        fields = ['id', 'nama', 'deskripsi', 'urutan', 'aktif']


class PetunjukSerializer(serializers.ModelSerializer):
    """Serializer untuk petunjuk yang akan digunakan Flutter frontend"""
    kategori_nama = serializers.CharField(source='kategori.nama', read_only=True)
    sudah_dibaca = serializers.SerializerMethodField()
    
    class Meta:
        model = Petunjuk
        fields = [
            'id', 'judul', 'kategori', 'kategori_nama', 'konten', 
            'langkah_langkah', 'gambar', 'urutan', 'aktif', 
            'created_at', 'updated_at', 'sudah_dibaca'
        ]
    
    def get_sudah_dibaca(self, obj):
        """Check if current user has read this petunjuk"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return PetunjukBaca.objects.filter(
                user=request.user, 
                petunjuk=obj
            ).exists()
        return False


class PetunjukBacaSerializer(serializers.ModelSerializer):
    """Serializer untuk tracking petunjuk yang sudah dibaca"""
    petunjuk_judul = serializers.CharField(source='petunjuk.judul', read_only=True)
    
    class Meta:
        model = PetunjukBaca
        fields = ['id', 'user', 'petunjuk', 'petunjuk_judul', 'tanggal_baca']
        read_only_fields = ['tanggal_baca']
