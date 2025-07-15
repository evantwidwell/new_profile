from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', blog_views.about, name='about'),
    path('projects/', blog_views.projects, name='projects'),
    path('taxi-viz/', blog_views.taxi_viz, name='taxi_viz'),
    path('api/', include('taxi_api.urls')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico')), name='favicon'),
    path('', blog_views.about, name='home'),
    path('<slug:slug>/', blog_views.post_detail, name='post_detail'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
