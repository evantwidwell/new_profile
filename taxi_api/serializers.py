from rest_framework import serializers
from .models import TaxiTrip, TaxiZone


class TaxiTripSerializer(serializers.ModelSerializer):
    trip_duration_minutes = serializers.ReadOnlyField()
    fare_per_mile = serializers.ReadOnlyField()
    
    class Meta:
        model = TaxiTrip
        fields = [
            'id',
            'vendor_id',
            'pickup_datetime',
            'dropoff_datetime',
            'passenger_count',
            'trip_distance',
            'pickup_longitude',
            'pickup_latitude',
            'dropoff_longitude',
            'dropoff_latitude',
            'pickup_location_id',
            'dropoff_location_id',
            'fare_amount',
            'extra',
            'mta_tax',
            'tip_amount',
            'tolls_amount',
            'total_amount',
            'payment_type',
            'trip_duration_minutes',
            'fare_per_mile',
        ]


class TaxiTripSummarySerializer(serializers.Serializer):
    """Serializer for aggregated trip data"""
    date = serializers.DateField()
    total_trips = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_fare = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_distance = serializers.FloatField()
    avg_tip = serializers.DecimalField(max_digits=10, decimal_places=2)


class TaxiZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxiZone
        fields = ['location_id', 'borough', 'zone', 'service_zone']


class HeatmapDataSerializer(serializers.Serializer):
    """Serializer for heatmap data"""
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    trip_count = serializers.IntegerField()
    avg_fare = serializers.DecimalField(max_digits=10, decimal_places=2)


class RevenueAnalyticsSerializer(serializers.Serializer):
    """Serializer for revenue analytics"""
    hour = serializers.IntegerField()
    day_of_week = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    trip_count = serializers.IntegerField()
    avg_fare = serializers.DecimalField(max_digits=10, decimal_places=2)
