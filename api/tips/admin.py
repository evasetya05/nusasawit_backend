from django.contrib import admin
from .models import Tip, TipDiscussion

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'content',
        'category',
        'image_url',
        'contributor',
        'discussion',
        'created_at',
    )
    search_fields = ('title',)

@admin.register(TipDiscussion)
class TipDiscussionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tip', 'user_identifier', 'created_at')