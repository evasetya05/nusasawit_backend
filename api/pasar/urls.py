from django.urls import path

from .views import (
    MarketplaceItemCommentListCreateView,
    MarketplaceItemDetailView,
    MarketplaceItemListCreateView,
    MarketplaceItemMarkSoldView,
    marketplace_item_deep_link,
)

app_name = "api_pasar"

urlpatterns = [
    path("", MarketplaceItemListCreateView.as_view(), name="item_list_create"),
    path("<int:pk>/", MarketplaceItemDetailView.as_view(), name="item_detail"),
    path("<int:pk>/mark-sold/", MarketplaceItemMarkSoldView.as_view(), name="item_mark_sold"),
    path(
        "<int:pk>/comments/",
        MarketplaceItemCommentListCreateView.as_view(),
        name="item_comments",
    ),
    path("item/<int:pk>/", marketplace_item_deep_link, name="item_deep_link"),
]
