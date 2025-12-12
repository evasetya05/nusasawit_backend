from django.contrib import admin

from .models import ChatMessage, ChatThread


@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ["id", "admin", "supervisor", "subject", "updated_at"]
    list_filter = ["admin", "supervisor"]
    search_fields = [
        "subject",
        "admin__username",
        "admin__email",
        "supervisor__name",
    ]
    autocomplete_fields = ["admin", "supervisor"]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "thread", "sender_admin", "sender_supervisor", "created_at"]
    list_filter = ["created_at", "sender_admin"]
    search_fields = [
        "thread__subject",
        "thread__supervisor__name",
        "sender_admin__username",
        "content",
    ]
    autocomplete_fields = ["thread", "sender_admin", "sender_supervisor"]
