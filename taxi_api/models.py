from django.db import models
from django.utils import timezone


class TaxiTrip(models.Model):
    """
    Model for NYC Yellow Taxi trip data
    Based on: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
    """
    # Trip identification
    vendor_id = models.IntegerField()
    pickup_datetime = models.DateTimeField()
    dropoff_datetime = models.DateTimeField()
    
    # Trip details
    passenger_count = models.IntegerField()
    trip_distance = models.FloatField()
    
    # Location data
    pickup_longitude = models.FloatField(null=True, blank=True)
    pickup_latitude = models.FloatField(null=True, blank=True)
    dropoff_longitude = models.FloatField(null=True, blank=True)
    dropoff_latitude = models.FloatField(null=True, blank=True)
    
    # Location zones (newer data format)
    pickup_location_id = models.IntegerField(null=True, blank=True)
    dropoff_location_id = models.IntegerField(null=True, blank=True)
    
    # Payment and fare
    fare_amount = models.DecimalField(max_digits=10, decimal_places=2)
    extra = models.DecimalField(max_digits=10, decimal_places=2)
    mta_tax = models.DecimalField(max_digits=10, decimal_places=2)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tolls_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.IntegerField()
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-pickup_datetime']
        indexes = [
            models.Index(fields=['pickup_datetime']),
            models.Index(fields=['dropoff_datetime']),
            models.Index(fields=['pickup_location_id']),
            models.Index(fields=['dropoff_location_id']),
        ]
    
    def __str__(self):
        return f"Trip {self.id} - {self.pickup_datetime}"
    
    @property
    def trip_duration_minutes(self):
        """Calculate trip duration in minutes"""
        if self.pickup_datetime and self.dropoff_datetime:
            duration = self.dropoff_datetime - self.pickup_datetime
            return duration.total_seconds() / 60
        return None
    
    @property
    def fare_per_mile(self):
        """Calculate fare per mile"""
        if self.trip_distance and self.trip_distance > 0:
            return float(self.fare_amount) / self.trip_distance
        return None


class TaxiZone(models.Model):
    """
    Model for NYC Taxi Zone lookup data
    """
    location_id = models.IntegerField(unique=True)
    borough = models.CharField(max_length=100)
    zone = models.CharField(max_length=100)
    service_zone = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.zone} ({self.borough})"
