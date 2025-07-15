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
        
        # Extract the assets from the React build
        import re
        css_pattern = r'<link rel="stylesheet"[^>]*href="([^"]*)"'
        js_pattern = r'<script[^>]*src="([^"]*)"'
        
        css_match = re.search(css_pattern, content)
        js_match = re.search(js_pattern, content)
        
        react_assets = ""
        if css_match:
            css_path = css_match.group(1).replace(
                '/assets/', '/static/taxi-viz/assets/'
            )
            react_assets += (
                f'<link rel="stylesheet" crossorigin href="{css_path}">\n'
            )
        
        if js_match:
            js_path = js_match.group(1).replace(
                '/assets/', '/static/taxi-viz/assets/'
            )
            react_assets += (
                f'<script type="module" crossorigin '
                f'src="{js_path}"></script>\n'
            )
        
        return render(request, 'blog/taxi_viz.html', {
            'react_assets': react_assets
        })
    else:
        return HttpResponse("Taxi visualization app not found", status=404)
