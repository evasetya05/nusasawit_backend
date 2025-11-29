from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .models import Petunjuk, PetunjukKategori, PetunjukBaca
from .serializers import (
    PetunjukSerializer, PetunjukKategoriSerializer, PetunjukBacaSerializer
)
from api.permission import HasValidAppKey


@api_view(['GET', 'POST'])
@permission_classes([HasValidAppKey])
def petunjuk_list(request):
    """List all petunjuk or create new petunjuk"""
    if request.method == 'GET':
        # Filter by active status and category if provided
        petunjuk_queryset = Petunjuk.objects.filter(aktif=True)
        
        kategori_id = request.GET.get('kategori')
        if kategori_id:
            petunjuk_queryset = petunjuk_queryset.filter(kategori_id=kategori_id)
            
        petunjuk_queryset = petunjuk_queryset.select_related('kategori').order_by(
            'kategori__urutan', 'kategori__nama', 'urutan', 'judul'
        )
        
        serializer = PetunjukSerializer(
            petunjuk_queryset, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = PetunjukSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([HasValidAppKey])
def petunjuk_detail(request, pk):
    """Get, update or delete specific petunjuk"""
    try:
        petunjuk = Petunjuk.objects.get(pk=pk)
    except Petunjuk.DoesNotExist:
        return Response({'error': 'Petunjuk not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PetunjukSerializer(petunjuk, context={'request': request})
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = PetunjukSerializer(petunjuk, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        petunjuk.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([HasValidAppKey])
def kategori_list(request):
    """List all kategori or create new kategori"""
    if request.method == 'GET':
        kategori = PetunjukKategori.objects.filter(aktif=True).order_by('urutan', 'nama')
        serializer = PetunjukKategoriSerializer(kategori, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = PetunjukKategoriSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasValidAppKey])
def mark_as_read(request, petunjuk_id):
    """Mark petunjuk as read by user"""
    try:
        petunjuk = Petunjuk.objects.get(pk=petunjuk_id)
    except Petunjuk.DoesNotExist:
        return Response({'error': 'Petunjuk not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get user from request (assuming user is authenticated)
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Create or get existing read record
    petunjuk_baca, created = PetunjukBaca.objects.get_or_create(
        user=request.user,
        petunjuk=petunjuk
    )
    
    serializer = PetunjukBacaSerializer(petunjuk_baca)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([HasValidAppKey])
def user_read_history(request):
    """Get user's petunjuk read history"""
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    read_history = PetunjukBaca.objects.filter(
        user=request.user
    ).select_related('petunjuk', 'petunjuk__kategori').order_by('-tanggal_baca')
    
    serializer = PetunjukBacaSerializer(read_history, many=True)
    return Response(serializer.data)
