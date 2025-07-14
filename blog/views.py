from django.shortcuts import render, get_object_or_404
from .models import Post


def post_list(request):
    posts = Post.objects.order_by('-date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/post_detail.html', {'post': post})


def testing(request):
    return render(request, 'blog/testing.html')


def testing2(request):
    return render(request, 'blog/testing2.html')

def testing3(request):
    return render(request, 'blog/testing3.html')


def about(request):
    return render(request, 'blog/about.html')


def projects(request):
    return render(request, 'blog/projects.html')