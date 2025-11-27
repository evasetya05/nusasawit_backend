from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BlogForm
from .models import Blog  # Import the Blog model from models.py

@login_required
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.penulis = request.user
            blog.save()
            messages.success(request, "Blog berhasil di-post!")
            form = BlogForm()  # Reset form after saving
    else:
        form = BlogForm()

    return render(request, 'blog/create_blog.html', {'form': form})


def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'blogs': blogs})


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)  # Menangkap blog berdasarkan slug
    return render(request, 'blog/blog_detail.html', {'blog': blog})
