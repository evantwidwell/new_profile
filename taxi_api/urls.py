from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'trips', views.TaxiTripViewSet)
router.register(r'zones', views.TaxiZoneViewSet)

app_name = 'taxi_api'

urlpatterns = [
    path('', include(router.urls)),
]
