import duckdb
from typing import Dict, List


class TaxiDataService:
    """
    Service to query NYC Taxi data directly from parquet files using DuckDB
    No need to load into PostgreSQL - query on demand!
    """
    
    def __init__(self):
        self.conn = duckdb.connect()
        self.base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
        self.data_cache = {}
    
    def get_parquet_url(self, year: int, month: int,
                        taxi_type: str = 'yellow') -> str:
        """Get the URL for a specific parquet file"""
        return (f"{self.base_url}/{taxi_type}_tripdata_"
                f"{year}-{month:02d}.parquet")
    
    def create_temp_table(self, year: int, month: int,
                          taxi_type: str = 'yellow') -> str:
        """Create a temporary table from parquet file"""
        url = self.get_parquet_url(year, month, taxi_type)
        table_name = f"trips_{taxi_type}_{year}_{month:02d}"
        
        # Create table directly from parquet URL
        query = f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT
            tpep_pickup_datetime as pickup_datetime,
            tpep_dropoff_datetime as dropoff_datetime,
            passenger_count,
            trip_distance,
            PULocationID as pickup_location_id,
            DOLocationID as dropoff_location_id,
            fare_amount,
            tip_amount,
            total_amount,
            payment_type
        FROM read_parquet('{url}')
        WHERE pickup_datetime IS NOT NULL
        """
        
        try:
            self.conn.execute(query)
            return table_name
        except Exception as e:
            print(f"Error creating table from {url}: {e}")
            return None
    
    def get_trip_summary(self, year: int, month: int,
                         limit: int = 30) -> List[Dict]:
        """Get daily trip summary statistics"""
        table_name = self.create_temp_table(year, month)
        if not table_name:
            return []
        
        query = f"""
        SELECT
            DATE(pickup_datetime) as date,
            COUNT(*) as total_trips,
            SUM(total_amount) as total_revenue,
            AVG(fare_amount) as avg_fare,
            AVG(trip_distance) as avg_distance,
            AVG(tip_amount) as avg_tip,
            AVG(passenger_count) as avg_passengers
        FROM {table_name}
        GROUP BY DATE(pickup_datetime)
        ORDER BY date DESC
        LIMIT {limit}
        """
        
        result = self.conn.execute(query).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        
        return [dict(zip(columns, row)) for row in result]
    
    def get_heatmap_data(self, year: int, month: int,
                         limit: int = 1000) -> List[Dict]:
        """Get pickup location data for heatmap (using zone IDs)"""
        table_name = self.create_temp_table(year, month)
        if not table_name:
            return []
        
        query = f"""
        SELECT
            pickup_location_id,
            COUNT(*) as trip_count,
            AVG(fare_amount) as avg_fare,
            AVG(trip_distance) as avg_distance
        FROM {table_name}
        WHERE pickup_location_id IS NOT NULL
        GROUP BY pickup_location_id
        ORDER BY trip_count DESC
        LIMIT {limit}
        """
        
        result = self.conn.execute(query).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        
        return [dict(zip(columns, row)) for row in result]
    
    def get_revenue_analytics(self, year: int, month: int) -> Dict:
        """Get revenue analytics by hour, day of week, etc."""
        table_name = self.create_temp_table(year, month)
        if not table_name:
            return {}
        
        # Revenue by hour
        hourly_query = f"""
        SELECT
            EXTRACT(HOUR FROM pickup_datetime) as hour,
            COUNT(*) as trips,
            SUM(total_amount) as revenue,
            AVG(fare_amount) as avg_fare
        FROM {table_name}
        GROUP BY EXTRACT(HOUR FROM pickup_datetime)
        ORDER BY hour
        """
        
        # Revenue by day of week
        daily_query = f"""
        SELECT
            EXTRACT(DOW FROM pickup_datetime) as day_of_week,
            COUNT(*) as trips,
            SUM(total_amount) as revenue,
            AVG(fare_amount) as avg_fare
        FROM {table_name}
        GROUP BY EXTRACT(DOW FROM pickup_datetime)
        ORDER BY day_of_week
        """
        
        hourly_result = self.conn.execute(hourly_query).fetchall()
        daily_result = self.conn.execute(daily_query).fetchall()
        
        return {
            'hourly': [
                {'hour': row[0], 'trips': row[1], 'revenue': row[2], 
                 'avg_fare': row[3]}
                for row in hourly_result
            ],
            'daily': [
                {'day': row[0], 'trips': row[1], 'revenue': row[2], 
                 'avg_fare': row[3]}
                for row in daily_result
            ]
        }
    
    def get_trip_stats(self, year: int, month: int) -> Dict:
        """Get basic trip statistics"""
        table_name = self.create_temp_table(year, month)
        if not table_name:
            return {}
        
        query = f"""
        SELECT
            COUNT(*) as total_trips,
            SUM(total_amount) as total_revenue,
            AVG(fare_amount) as avg_fare,
            AVG(trip_distance) as avg_distance,
            AVG(tip_amount) as avg_tip,
            MIN(pickup_datetime) as earliest_trip,
            MAX(pickup_datetime) as latest_trip,
            COUNT(DISTINCT pickup_location_id) as unique_pickup_locations,
            COUNT(DISTINCT dropoff_location_id) as unique_dropoff_locations
        FROM {table_name}
        """
        
        result = self.conn.execute(query).fetchone()
        columns = [desc[0] for desc in self.conn.description]
        
        return dict(zip(columns, result))
    
    def get_sample_trips(self, year: int, month: int, 
                        limit: int = 100) -> List[Dict]:
        """Get sample trips for display"""
        table_name = self.create_temp_table(year, month)
        if not table_name:
            return []
        
        query = f"""
        SELECT
            pickup_datetime,
            dropoff_datetime,
            passenger_count,
            trip_distance,
            pickup_location_id,
            dropoff_location_id,
            fare_amount,
            tip_amount,
            total_amount
        FROM {table_name}
        ORDER BY pickup_datetime DESC
        LIMIT {limit}
        """
        
        result = self.conn.execute(query).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        
        return [dict(zip(columns, row)) for row in result]
    
    def close(self):
        """Close the DuckDB connection"""
        if self.conn:
            self.conn.close()
