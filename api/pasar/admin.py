from django.contrib import admin

from .models import MarketplaceComment, MarketplaceItem


@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "price",
        "is_sold",
        "seller_identifier",
        "created_at",
    )
    list_filter = ("is_sold", "created_at")
    search_fields = ("title", "description", "seller_identifier")
    readonly_fields = ("created_at", "updated_at", "sold_at")


@admin.register(MarketplaceComment)
class MarketplaceCommentAdmin(admin.ModelAdmin):
    list_display = ("item", "buyer_identifier", "is_purchase_intent", "created_at")
    list_filter = ("is_purchase_intent", "created_at")
    search_fields = ("message", "buyer_identifier")
    readonly_fields = ("created_at",)
