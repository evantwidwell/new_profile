from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', blog_views.post_list, name='home'),
    path('<slug:slug>/', blog_views.post_detail, name='post_detail'),
    path('testing/', blog_views.testing, name='testing'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico')), name='favicon'),
]
