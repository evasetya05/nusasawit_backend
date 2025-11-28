from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.permission import HasValidAppKey
from .models import CertificationProgress, CertificationTask
from .serializers import CertificationProgressSerializer, CertificationTaskSerializer


class FarmerCertificationListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasValidAppKey]
    serializer_class = CertificationProgressSerializer

    def get_queryset(self):
        return CertificationProgress.objects.filter(farmer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)


class CertificationProgressDetailView(generics.RetrieveAPIView):
    permission_classes = [HasValidAppKey]
    queryset = CertificationProgress.objects.all()
    serializer_class = CertificationProgressSerializer


class CertificationTaskCreateView(generics.CreateAPIView):
    permission_classes = [HasValidAppKey]
    serializer_class = CertificationTaskSerializer

    def perform_create(self, serializer):
        progress_id = self.kwargs.get("pk")
        progress = CertificationProgress.objects.get(id=progress_id)
        serializer.save(certification=progress)
