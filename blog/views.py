from django.shortcuts import render, get_object_or_404
from django.conf import settings
import logging
from .models import Post

logger = logging.getLogger(__name__)

def post_list(request):
    try:
        logger.debug("Attempting to fetch posts")
        posts = Post.objects.order_by('-date')
        logger.debug(f"Found {posts.count()} posts")
        
        if not posts.exists():
            logger.debug("No posts found, rendering empty template")
            return render(request, 'blog/post_list.html', {
                'posts': [],
                'message': 'No posts yet. Check back soon!'
            })
        
        logger.debug("Rendering template with posts")
        return render(request, 'blog/post_list.html', {'posts': posts})
    except Exception as e:
        logger.error(f"Error in post_list view: {str(e)}", exc_info=True)
        if settings.DEBUG:
            raise e
        return render(request, 'blog/post_list.html', {
            'posts': [],
            'error': 'Unable to load posts'
        })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/post_detail.html', {'post': post})
