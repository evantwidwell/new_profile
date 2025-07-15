from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from .models import Post
import os


def post_list(request):
    posts = Post.objects.order_by('-date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/post_detail.html', {'post': post})


def about(request):
    return render(request, 'blog/about.html')


def projects(request):
    return render(request, 'blog/projects.html')


def taxi_viz(request):
    """Serve the React taxi visualization app"""
    static_dir = os.path.join(settings.BASE_DIR, 'blog', 'static', 'taxi-viz')
    index_path = os.path.join(static_dir, 'index.html')
    
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Fix asset paths to use Django static files
        content = content.replace('/assets/', '/static/taxi-viz/assets/')
        content = content.replace('/vite.svg', '/static/taxi-viz/vite.svg')
        
        return HttpResponse(content, content_type='text/html')
    else:
        return HttpResponse("Taxi visualization app not found", status=404)