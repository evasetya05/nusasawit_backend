from rest_framework import serializers

from .models import MarketplaceComment, MarketplaceItem


class MarketplaceItemSerializer(serializers.ModelSerializer):
    photo_1_url = serializers.SerializerMethodField()
    photo_2_url = serializers.SerializerMethodField()

    class Meta:
        model = MarketplaceItem
        fields = [
            "id",
            "title",
            "description",
            "price",
            "photo_1",
            "photo_2",
            "photo_1_url",
            "photo_2_url",
            "is_sold",
            "sold_at",
            "seller_identifier",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "is_sold",
            "sold_at",
            "seller_identifier",
            "created_at",
            "updated_at",
            "photo_1_url",
            "photo_2_url",
        ]

    def _build_photo_url(self, obj, attr: str) -> str | None:
        photo = getattr(obj, attr)
        if not photo:
            return None
        request = self.context.get("request")
        url = photo.url
        if request:
            return request.build_absolute_uri(url)
        return url

    def get_photo_1_url(self, obj):
        return self._build_photo_url(obj, "photo_1")

    def get_photo_2_url(self, obj):
        return self._build_photo_url(obj, "photo_2")

    def create(self, validated_data):
        request = self.context.get("request")
        seller = getattr(request, "flutter_user", None) if request else None
        identifier = getattr(request, "flutter_user_identifier", "") if request else ""

        validated_data.setdefault("seller", seller)
        validated_data.setdefault("seller_identifier", identifier or "")
        return super().create(validated_data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        photo_1 = attrs.get("photo_1")
        photo_2 = attrs.get("photo_2")

        if self.instance:
            photo_1 = photo_1 or getattr(self.instance, "photo_1")
            photo_2 = photo_2 or getattr(self.instance, "photo_2")

        if not photo_1 and not photo_2:
            raise serializers.ValidationError("Minimal satu foto harus diunggah.")

        return attrs


class MarketplaceCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceComment
        fields = [
            "id",
            "item",
            "message",
            "is_purchase_intent",
            "buyer_identifier",
            "created_at",
        ]
        read_only_fields = ["item", "buyer_identifier", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        buyer = getattr(request, "flutter_user", None) if request else None
        identifier = getattr(request, "flutter_user_identifier", "") if request else ""

        validated_data.setdefault("flutter_user", buyer)
        validated_data.setdefault("buyer_identifier", identifier or "")
        return super().create(validated_data)

    def save(self, **kwargs):
        # allow passing item through serializer.save(item=...)
        if "item" in kwargs:
            self.validated_data["item"] = kwargs.pop("item")
        return super().save(**kwargs)


class MarketplaceItemDetailSerializer(MarketplaceItemSerializer):
    comments = MarketplaceCommentSerializer(many=True, read_only=True)

    class Meta(MarketplaceItemSerializer.Meta):
        fields = MarketplaceItemSerializer.Meta.fields + ["comments"]
