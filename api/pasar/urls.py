from django.urls import path

from .views import (
    MarketplaceItemCommentListCreateView,
    MarketplaceItemDetailView,
    MarketplaceItemListCreateView,
    MarketplaceItemMarkSoldView,
)

app_name = "pasar"

urlpatterns = [
    path("", MarketplaceItemListCreateView.as_view(), name="item_list_create"),
    path("<int:pk>/", MarketplaceItemDetailView.as_view(), name="item_detail"),
    path("<int:pk>/mark-sold/", MarketplaceItemMarkSoldView.as_view(), name="item_mark_sold"),
    path(
        "<int:pk>/comments/",
        MarketplaceItemCommentListCreateView.as_view(),
        name="item_comments",
    ),
]
