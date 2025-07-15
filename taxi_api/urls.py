from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .duckdb_views import (
    TripSummaryView, HeatmapDataView, RevenueAnalyticsView,
    TripStatsView, SampleTripsView, DataStatusView
)

router = DefaultRouter()
router.register(r'trips', views.TaxiTripViewSet)
router.register(r'zones', views.TaxiZoneViewSet)

app_name = 'taxi_api'

urlpatterns = [
    path('', include(router.urls)),
    
    # DuckDB-based endpoints (no database storage needed!)
    path('taxi-data/summary/', TripSummaryView.as_view(),
         name='trip-summary'),
    path('taxi-data/heatmap/', HeatmapDataView.as_view(),
         name='heatmap-data'),
    path('taxi-data/revenue/', RevenueAnalyticsView.as_view(),
         name='revenue-analytics'),
    path('taxi-data/stats/', TripStatsView.as_view(),
         name='trip-stats'),
    path('taxi-data/trips/', SampleTripsView.as_view(),
         name='sample-trips'),
    path('taxi-data/status/', DataStatusView.as_view(),
         name='data-status'),
]
