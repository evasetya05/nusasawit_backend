from django.contrib import admin
from .models import Blog
from django.utils.text import slugify

class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug", "penulis", "created_at")
    search_fields = ("title", "content")
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = slugify(obj.title)
            slug = base_slug
            counter = 1

            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            obj.slug = slug
        super().save_model(request, obj, form, change)

admin.site.register(Blog, BlogAdmin)
