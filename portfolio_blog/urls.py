from django.contrib import admin
from django.urls import path
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', blog_views.post_list, name='home'),
    path('<slug:slug>/', blog_views.post_detail, name='post_detail'),
]
