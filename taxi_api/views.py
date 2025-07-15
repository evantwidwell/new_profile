from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncDate, Extract
from .models import TaxiTrip, TaxiZone
from .serializers import (
    TaxiTripSerializer,
    TaxiTripSummarySerializer,
    TaxiZoneSerializer,
    HeatmapDataSerializer,
    RevenueAnalyticsSerializer
)


class TaxiTripViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for NYC Taxi trip data
    """
    queryset = TaxiTrip.objects.all()
    serializer_class = TaxiTripSerializer
    
    def get_queryset(self):
        """
        Filter trips by date range, location, etc.
        """
        queryset = TaxiTrip.objects.all()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(pickup_datetime__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(pickup_datetime__date__lte=end_date)
        
        # Filter by pickup location
        pickup_location = self.request.query_params.get('pickup_location')
        if pickup_location:
            queryset = queryset.filter(pickup_location_id=pickup_location)
        
        # Filter by minimum fare
        min_fare = self.request.query_params.get('min_fare')
        if min_fare:
            queryset = queryset.filter(fare_amount__gte=min_fare)
        
        return queryset.order_by('-pickup_datetime')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get daily trip summary statistics
        """
        queryset = self.get_queryset()
        
        # Group by date and calculate aggregates
        summary_data = (
            queryset
            .annotate(date=TruncDate('pickup_datetime'))
            .values('date')
            .annotate(
                total_trips=Count('id'),
                total_revenue=Sum('total_amount'),
                avg_fare=Avg('fare_amount'),
                avg_distance=Avg('trip_distance'),
                avg_tip=Avg('tip_amount')
            )
            .order_by('-date')
        )
        
        serializer = TaxiTripSummarySerializer(summary_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def heatmap(self, request):
        """
        Get pickup location data for heatmap visualization
        """
        queryset = self.get_queryset()
        
        # Group by pickup coordinates and calculate metrics
        heatmap_data = (
            queryset
            .filter(
                pickup_latitude__isnull=False,
                pickup_longitude__isnull=False
            )
            .values('pickup_latitude', 'pickup_longitude')
            .annotate(
                trip_count=Count('id'),
                avg_fare=Avg('fare_amount')
            )
            .order_by('-trip_count')[:1000]  # Limit to top 1000 locations
        )
        
        # Transform to expected format
        formatted_data = [
            {
                'latitude': item['pickup_latitude'],
                'longitude': item['pickup_longitude'],
                'trip_count': item['trip_count'],
                'avg_fare': item['avg_fare']
            }
            for item in heatmap_data
        ]
        
        serializer = HeatmapDataSerializer(formatted_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def revenue_analytics(self, request):
        """
        Get revenue analytics by hour and day of week
        """
        queryset = self.get_queryset()
        
        # Group by hour and day of week
        analytics_data = (
            queryset
            .annotate(
                hour=Extract('pickup_datetime', 'hour'),
                day_of_week=Extract('pickup_datetime', 'week_day')
            )
            .values('hour', 'day_of_week')
            .annotate(
                total_revenue=Sum('total_amount'),
                trip_count=Count('id'),
                avg_fare=Avg('fare_amount')
            )
            .order_by('day_of_week', 'hour')
        )
        
        serializer = RevenueAnalyticsSerializer(analytics_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get overall statistics
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_trips': queryset.count(),
            'avg_fare': queryset.aggregate(Avg('fare_amount'))['fare_amount__avg'],
            'avg_distance': queryset.aggregate(Avg('trip_distance'))['trip_distance__avg'],
            'avg_tip': queryset.aggregate(Avg('tip_amount'))['tip_amount__avg'],
            'total_revenue': queryset.aggregate(Sum('total_amount'))['total_amount__sum'],
            'avg_passenger_count': queryset.aggregate(Avg('passenger_count'))['passenger_count__avg'],
        }
        
        return Response(stats)


class TaxiZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for NYC Taxi zone data
    """
    queryset = TaxiZone.objects.all()
    serializer_class = TaxiZoneSerializer
