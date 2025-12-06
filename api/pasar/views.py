from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permission import HasValidAppKey

from .models import MarketplaceComment, MarketplaceItem
from .serializers import (
    MarketplaceCommentSerializer,
    MarketplaceItemDetailSerializer,
    MarketplaceItemSerializer,
)


class MarketplaceItemListCreateView(generics.ListCreateAPIView):
    queryset = MarketplaceItem.objects.all().order_by("-created_at")
    serializer_class = MarketplaceItemSerializer
    permission_classes = [HasValidAppKey]

    def get_queryset(self):
        queryset = super().get_queryset()
        show_sold = self.request.query_params.get("show_sold")
        if show_sold is None or str(show_sold).lower() in ("false", "0", "no"):
            queryset = queryset.filter(is_sold=False)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class MarketplaceItemDetailView(generics.RetrieveAPIView):
    queryset = MarketplaceItem.objects.all()
    serializer_class = MarketplaceItemDetailSerializer
    permission_classes = [HasValidAppKey]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class MarketplaceItemMarkSoldView(APIView):
    permission_classes = [HasValidAppKey]

    def post(self, request, pk):
        item = get_object_or_404(MarketplaceItem, pk=pk)

        identifier = getattr(request, "flutter_user_identifier", None)
        flutter_user = getattr(request, "flutter_user", None)

        if item.seller_identifier and identifier and identifier != item.seller_identifier:
            return Response(
                {"detail": "Anda tidak diizinkan memperbarui status barang ini."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if item.seller and flutter_user and item.seller_id != flutter_user.id:
            return Response(
                {"detail": "Anda tidak diizinkan memperbarui status barang ini."},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_sold = request.data.get("is_sold", True)
        if isinstance(is_sold, str):
            is_sold = str(is_sold).lower() in ("1", "true", "yes", "on")

        item.set_sold(bool(is_sold))
        serializer = MarketplaceItemDetailSerializer(item, context={"request": request})
        return Response(serializer.data)


class MarketplaceItemCommentListCreateView(APIView):
    permission_classes = [HasValidAppKey]

    def get(self, request, pk):
        item = get_object_or_404(MarketplaceItem, pk=pk)
        comments = item.comments.all().order_by("created_at")
        serializer = MarketplaceCommentSerializer(
            comments, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request, pk):
        item = get_object_or_404(MarketplaceItem, pk=pk)
        serializer = MarketplaceCommentSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(item=item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
