import duckdb
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class SimpleTestView(APIView):
    """
    Simple test view to check if DuckDB is working
    """

    def get(self, request):
        try:
            # Test basic DuckDB connection
            conn = duckdb.connect()
            result = conn.execute("SELECT 1 as test").fetchone()
            conn.close()

            return Response(
                {
                    "status": "success",
                    "duckdb_test": result[0],
                    "message": "DuckDB is working!",
                }
            )
        except Exception as e:
            return Response(
                {"status": "error", "error": str(e), "message": "DuckDB test failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TaxiDataService:
    """
    Simplified service for testing
    """

    def __init__(self):
        self.conn = duckdb.connect()
        self.base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"

    def get_parquet_url(self, year: int, month: int) -> str:
        """Get the URL for a specific parquet file"""
        return f"{self.base_url}/yellow_tripdata_{year}-{month:02d}.parquet"

    def test_parquet_access(self, year: int, month: int):
        """Test if we can access a parquet file"""
        url = self.get_parquet_url(year, month)
        try:
            # Just try to read the first row to test access
            result = self.conn.execute(
                f"SELECT COUNT(*) FROM read_parquet('{url}') LIMIT 1"
            ).fetchone()
            return {"success": True, "count": result[0], "url": url}
        except Exception as e:
            return {"success": False, "error": str(e), "url": url}

    def close(self):
        if self.conn:
            self.conn.close()


class TaxiTestView(APIView):
    """
    Test view for taxi data access
    """

    def get(self, request):
        year = int(request.GET.get("year", 2023))
        month = int(request.GET.get("month", 1))

        service = TaxiDataService()
        try:
            result = service.test_parquet_access(year, month)
            return Response({"year": year, "month": month, "result": result})
        except Exception as e:
            return Response(
                {"error": str(e), "year": year, "month": month},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            service.close()
