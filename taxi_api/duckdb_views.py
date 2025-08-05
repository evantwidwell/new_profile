from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import TaxiDataService


class TaxiDataAPIView(APIView):
    """
    Base API view for taxi data using DuckDB service
    """

    def get_year_month(self, request):
        """Extract year and month from request parameters"""
        year = int(request.GET.get("year", 2023))
        month = int(request.GET.get("month", 1))
        return year, month


class TripSummaryView(TaxiDataAPIView):
    """
    GET /api/taxi-data/summary/
    Get daily trip summary statistics
    """

    def get(self, request):
        year, month = self.get_year_month(request)
        limit = int(request.GET.get("limit", 30))

        service = TaxiDataService()
        try:
            data = service.get_trip_summary(year, month, limit)
            return Response({"year": year, "month": month, "data": data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            service.close()


class HeatmapDataView(TaxiDataAPIView):
    """
    GET /api/taxi-data/heatmap/
    Get pickup location data for heatmap
    """

    def get(self, request):
        year, month = self.get_year_month(request)
        limit = int(request.GET.get("limit", 1000))

        service = TaxiDataService()
        try:
            data = service.get_heatmap_data(year, month, limit)
            return Response({"year": year, "month": month, "data": data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            service.close()


class RevenueAnalyticsView(TaxiDataAPIView):
    """
    GET /api/taxi-data/revenue/
    Get revenue analytics by hour and day of week
    """

    def get(self, request):
        year, month = self.get_year_month(request)

        service = TaxiDataService()
        try:
            data = service.get_revenue_analytics(year, month)
            return Response({"year": year, "month": month, "data": data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            service.close()


class TripStatsView(TaxiDataAPIView):
    """
    GET /api/taxi-data/stats/
    Get basic trip statistics
    """

    def get(self, request):
        year, month = self.get_year_month(request)

        service = TaxiDataService()
        try:
            data = service.get_trip_stats(year, month)
            return Response({"year": year, "month": month, "data": data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            service.close()


class SampleTripsView(TaxiDataAPIView):
    """
    GET /api/taxi-data/trips/
    Get sample trips for display
    """

    def get(self, request):
        year, month = self.get_year_month(request)
        limit = int(request.GET.get("limit", 100))

        service = TaxiDataService()
        try:
            data = service.get_sample_trips(year, month, limit)
            return Response(
                {"year": year, "month": month, "count": len(data), "data": data}
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            service.close()


class DataStatusView(APIView):
    """
    GET /api/taxi-data/status/
    Check what data is available
    """

    def get(self, request):
        # Return available years and months
        available_data = []

        # For now, just return some known available data
        for year in [2023, 2024]:
            for month in range(1, 13):
                available_data.append(
                    {
                        "year": year,
                        "month": month,
                        "url": (
                            f"https://d37ci6vzurychx.cloudfront.net/"
                            f"trip-data/yellow_tripdata_{year}-{month:02d}"
                            f".parquet"
                        ),
                    }
                )

        return Response(
            {
                "available_data": available_data,
                "message": (
                    "Data is queried directly from parquet files - "
                    "no database storage needed!"
                ),
            }
        )
