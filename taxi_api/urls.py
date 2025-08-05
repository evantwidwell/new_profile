from django.urls import path

from .duckdb_views import (
    DataStatusView,
    HeatmapDataView,
    RevenueAnalyticsView,
    SampleTripsView,
    TripStatsView,
    TripSummaryView,
)
from .test_views import SimpleTestView, TaxiTestView

app_name = "taxi_api"

urlpatterns = [
    # Test endpoints for debugging
    path("test/", SimpleTestView.as_view(), name="simple-test"),
    path("test/taxi/", TaxiTestView.as_view(), name="taxi-test"),
    # DuckDB-based endpoints (no database storage needed!)
    path("taxi-data/summary/", TripSummaryView.as_view(), name="trip-summary"),
    path("taxi-data/heatmap/", HeatmapDataView.as_view(), name="heatmap-data"),
    path(
        "taxi-data/revenue/", RevenueAnalyticsView.as_view(), name="revenue-analytics"
    ),
    path("taxi-data/stats/", TripStatsView.as_view(), name="trip-stats"),
    path("taxi-data/trips/", SampleTripsView.as_view(), name="sample-trips"),
    path("taxi-data/status/", DataStatusView.as_view(), name="data-status"),
]
