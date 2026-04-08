from django.contrib import admin
from .models import Tip, TipDiscussion

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'contributor')
    search_fields = ('title',)

@admin.register(TipDiscussion)
class TipDiscussionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tip', 'user_identifier', 'created_at')