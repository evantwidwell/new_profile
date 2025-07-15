from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', blog_views.about, name='about'),
    path('projects/', blog_views.projects, name='projects'),

    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico')), name='favicon'),
    path('', blog_views.about, name='home'),
    path('<slug:slug>/', blog_views.post_detail, name='post_detail'),
]
