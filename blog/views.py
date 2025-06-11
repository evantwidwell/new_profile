from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Post


def post_list(request):
    try:
        posts = Post.objects.order_by('-date')
        if not posts.exists():
            return render(request, 'blog/post_list.html', {
                'posts': [],
                'message': 'No posts yet. Check back soon!'
            })
        return render(request, 'blog/post_list.html', {'posts': posts})
    except Exception as e:
        if settings.DEBUG:
            raise e
        return render(request, 'blog/post_list.html', {
            'posts': [],
            'error': 'Unable to load posts'
        })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/post_detail.html', {'post': post})
