from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', blog_views.about, name='about'),
    path('projects/', blog_views.projects, name='projects'),
    path('testing/', blog_views.testing, name='testing'),
    path('testing2/', blog_views.testing2, name='testing2'),
    path('testing3/', blog_views.testing3, name='testing3'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico')), name='favicon'),
    path('', blog_views.post_list, name='home'),
    path('<slug:slug>/', blog_views.post_detail, name='post_detail'),
]
