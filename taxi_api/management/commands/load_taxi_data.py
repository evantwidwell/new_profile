import os
import time
from decimal import Decimal

import duckdb
import requests
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError

from taxi_api.models import TaxiTrip, TaxiZone


class Command(BaseCommand):
    help = "Load NYC Taxi data from parquet files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10000,
            help="Number of records to process in each batch (default: 10000)",
        )
        parser.add_argument(
            "--get-all",
            action="store_true",
            help="Load all records instead of sampling",
        )
        parser.add_argument("--sample-size", type=int, help="Number of records to load")
        parser.add_argument(
            "--year",
            type=int,
            default=2023,
            help="Year of data to load (default: 2024)",
        )
        parser.add_argument(
            "--month", type=int, default=1, help="Month of data to load (default: 1)"
        )
        parser.add_argument(
            "--clear-data",
            action="store_true",
            help="Clear existing data before loading",
        )

    def handle(self, *args, **options):
        sample_size = options["sample_size"]
        year = options["year"]
        month = options["month"]
        clear_data = options["clear_data"]
        get_all = options["get_all"]
        batch_size = options["batch_size"]

        # Wait for database to be ready
        self.wait_for_db()

        if clear_data:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            TaxiTrip.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing data cleared."))

        # Load taxi zone data first
        self.load_taxi_zones()

        # Load trip data
        self.load_trip_data(year, month, sample_size, get_all, batch_size)

    def wait_for_db(self):
        """Wait for database to be available"""
        max_retries = 30
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                connection.ensure_connection()
                self.stdout.write(
                    self.style.SUCCESS("Database connection established.")
                )
                return
            except OperationalError as e:
                if attempt == max_retries - 1:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Database connection failed after {max_retries} attempts: "
                            f"{str(e)}"
                        )
                    )
                    raise

                self.stdout.write(
                    self.style.WARNING(
                        f"Database not ready (attempt {attempt + 1}/{max_retries}). "
                        f"Waiting {retry_delay}s..."
                    )
                )
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 10)  # Exponential backoff, max 10s

    def load_taxi_zones(self):
        """Load taxi zone lookup data"""
        self.stdout.write("Loading taxi zones...")

        # NYC taxi zones CSV URL
        zones_url = (
            "https://d37ci6vzurychx.cloudfront.net/misc/" "taxi+_zone_lookup.csv"
        )

        try:
            response = requests.get(zones_url)
            response.raise_for_status()

            # Save to temporary file
            with open("/tmp/taxi_zones.csv", "wb") as f:
                f.write(response.content)

            # Use DuckDB to read CSV
            conn = duckdb.connect()
            zones_data = conn.execute(
                "SELECT * FROM read_csv_auto('/tmp/taxi_zones.csv')"
            ).fetchall()

            # Get column names
            columns = [desc[0] for desc in conn.description]
            conn.close()

            # Clear existing zones
            TaxiZone.objects.all().delete()

            # Load zones
            zones_to_create = []
            for row in zones_data:
                row_dict = dict(zip(columns, row, strict=False))
                zone = TaxiZone(
                    location_id=row_dict["LocationID"],
                    borough=row_dict["Borough"],
                    zone=row_dict["Zone"],
                    service_zone=row_dict["service_zone"],
                )
                zones_to_create.append(zone)

            TaxiZone.objects.bulk_create(zones_to_create, batch_size=100)
            self.stdout.write(
                self.style.SUCCESS(f"Loaded {len(zones_to_create)} taxi zones")
            )

            # Clean up
            os.remove("/tmp/taxi_zones.csv")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading taxi zones: {str(e)}"))

    def load_trip_data(self, year, month, sample_size, get_all, batch_size):
        """Load trip data from NYC taxi dataset using DuckDB"""
        self.stdout.write(f"Loading trip data for {year}-{month:02d}...")

        # NYC Yellow Taxi parquet URL format
        url = (
            f"https://d37ci6vzurychx.cloudfront.net/trip-data/"
            f"yellow_tripdata_{year}-{month:02d}.parquet"
        )

        try:
            self.stdout.write(f"Downloading data from: {url}")

            # Download parquet file
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Save to temporary file
            temp_file = "/tmp/taxi_data.parquet"
            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Connect to DuckDB
            conn = duckdb.connect()

            # Get total number of records efficiently
            total_records = conn.execute(
                f"SELECT COUNT(*) FROM read_parquet('{temp_file}')"
            ).fetchone()[0]

            self.stdout.write(f"Total records in dataset: {total_records:,}")

            if get_all:
                self.stdout.write("Loading all records in batches...")
                records_to_process = total_records
                self.process_all_records(conn, temp_file, batch_size, total_records)
            elif sample_size:
                records_to_process = min(sample_size, total_records)
                self.stdout.write(f"Loading {records_to_process:,} records...")
                self.process_sample_records(conn, temp_file, sample_size, batch_size)
            else:
                # Smaller default sample
                records_to_process = min(1000, total_records)
                self.stdout.write(
                    f"Loading default sample of {records_to_process:,} " f"records..."
                )
                self.process_sample_records(conn, temp_file, 1000, batch_size)

            conn.close()

            # Clean up
            os.remove(temp_file)

            self.stdout.write(self.style.SUCCESS("Successfully loaded taxi data"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading trip data: {str(e)}"))

    def process_all_records(self, conn, temp_file, batch_size, total_records):
        """Process all records in batches using DuckDB"""
        num_batches = (total_records + batch_size - 1) // batch_size
        total_loaded = 0

        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_records)

            self.stdout.write(
                f"Processing batch {batch_idx + 1}/{num_batches}: "
                f"records {start_idx+1:,} to {end_idx:,}"
            )

            # Use DuckDB to read a chunk with data cleaning
            chunk_data = self.get_cleaned_chunk(conn, temp_file, start_idx, batch_size)

            if chunk_data:
                loaded_count = self.load_trips_to_db_duckdb(
                    chunk_data, batch_num=batch_idx + 1
                )
                total_loaded += loaded_count

            # Progress update
            progress = (end_idx / total_records) * 100
            self.stdout.write(
                f"Progress: {progress:.1f}% ({end_idx:,}/{total_records:,} " f"records)"
            )

        self.stdout.write(self.style.SUCCESS(f"Loaded {total_loaded:,} valid trips"))

    def process_sample_records(self, conn, temp_file, sample_size, batch_size):
        """Process a sample of records using DuckDB"""
        # Get sample data using DuckDB's SAMPLE function
        sample_data = self.get_cleaned_sample(conn, temp_file, sample_size)

        if not sample_data:
            self.stdout.write(self.style.WARNING("No valid data found"))
            return

        # Process in batches
        total_loaded = 0
        num_batches = (len(sample_data) + batch_size - 1) // batch_size

        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(sample_data))

            self.stdout.write(
                f"Processing batch {batch_idx + 1}/{num_batches}: "
                f"records {start_idx+1:,} to {end_idx:,}"
            )

            batch_data = sample_data[start_idx:end_idx]
            loaded_count = self.load_trips_to_db_duckdb(
                batch_data, batch_num=batch_idx + 1
            )
            total_loaded += loaded_count

        self.stdout.write(self.style.SUCCESS(f"Loaded {total_loaded:,} valid trips"))

    def get_cleaned_chunk(self, conn, temp_file, offset, limit):
        """Get a cleaned chunk of data using DuckDB"""
        query = f"""
        SELECT 
            VendorID as vendor_id,
            tpep_pickup_datetime as pickup_datetime,
            tpep_dropoff_datetime as dropoff_datetime,
            passenger_count,
            trip_distance,
            NULL as pickup_longitude,
            NULL as pickup_latitude,
            NULL as dropoff_longitude,
            NULL as dropoff_latitude,
            PULocationID as pickup_location_id,
            DOLocationID as dropoff_location_id,
            fare_amount,
            extra,
            mta_tax,
            tip_amount,
            tolls_amount,
            total_amount,
            payment_type
        FROM (
            SELECT * FROM read_parquet('{temp_file}')
            WHERE fare_amount >= 0 
              AND total_amount >= 0 
              AND trip_distance >= 0
              AND passenger_count > 0 
              AND passenger_count <= 9
            LIMIT {limit} OFFSET {offset}
        ) t
        """

        try:
            return conn.execute(query).fetchall()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error reading chunk: {str(e)}"))
            return []

    def get_cleaned_sample(self, conn, temp_file, sample_size):
        """Get a cleaned sample of data using DuckDB"""
        # Query adapted for the actual column structure
        query = f"""
        SELECT 
            VendorID as vendor_id,
            tpep_pickup_datetime as pickup_datetime,
            tpep_dropoff_datetime as dropoff_datetime,
            passenger_count,
            trip_distance,
            NULL as pickup_longitude,
            NULL as pickup_latitude,
            NULL as dropoff_longitude,
            NULL as dropoff_latitude,
            PULocationID as pickup_location_id,
            DOLocationID as dropoff_location_id,
            fare_amount,
            extra,
            mta_tax,
            tip_amount,
            tolls_amount,
            total_amount,
            payment_type
        FROM (
            SELECT * FROM read_parquet('{temp_file}')
            WHERE fare_amount >= 0 
              AND total_amount >= 0 
              AND trip_distance >= 0
              AND passenger_count > 0 
              AND passenger_count <= 9
            USING SAMPLE {sample_size}
        ) t
        """

        try:
            return conn.execute(query).fetchall()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error reading sample: {str(e)}"))
            return []

    def load_trips_to_db_duckdb(self, data, batch_num=None):
        """Load trips to database from DuckDB results with retry logic"""
        if batch_num:
            self.stdout.write(f"Loading batch {batch_num} to database...")
        else:
            self.stdout.write("Loading trips to database...")

        db_batch_size = 1000
        trips_to_create = []
        loaded_count = 0

        for row in data:
            try:
                trip = TaxiTrip(
                    vendor_id=int(row[0]) if row[0] else 1,
                    pickup_datetime=row[1],
                    dropoff_datetime=row[2],
                    passenger_count=int(row[3]) if row[3] else 1,
                    trip_distance=float(row[4]) if row[4] else 0,
                    pickup_longitude=row[5],
                    pickup_latitude=row[6],
                    dropoff_longitude=row[7],
                    dropoff_latitude=row[8],
                    pickup_location_id=int(row[9]) if row[9] else None,
                    dropoff_location_id=int(row[10]) if row[10] else None,
                    fare_amount=Decimal(str(row[11])) if row[11] else Decimal("0"),
                    extra=Decimal(str(row[12])) if row[12] else Decimal("0"),
                    mta_tax=Decimal(str(row[13])) if row[13] else Decimal("0"),
                    tip_amount=Decimal(str(row[14])) if row[14] else Decimal("0"),
                    tolls_amount=Decimal(str(row[15])) if row[15] else Decimal("0"),
                    total_amount=Decimal(str(row[16])) if row[16] else Decimal("0"),
                    payment_type=int(row[17]) if row[17] else 1,
                )
                trips_to_create.append(trip)

                # Batch insert with retry logic
                if len(trips_to_create) >= db_batch_size:
                    self.bulk_create_with_retry(trips_to_create, db_batch_size)
                    loaded_count += len(trips_to_create)
                    trips_to_create = []

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping invalid row in batch {batch_num or "N/A"}: '
                        f'{str(e)}'
                    )
                )
                continue

        # Insert remaining trips
        if trips_to_create:
            self.bulk_create_with_retry(trips_to_create, db_batch_size)
            loaded_count += len(trips_to_create)

        return loaded_count

    def bulk_create_with_retry(self, trips_to_create, batch_size):
        """Bulk create with retry logic for database connection issues"""
        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                TaxiTrip.objects.bulk_create(trips_to_create, batch_size=batch_size)
                return
            except OperationalError as e:
                if (
                    "not yet accepting connections" in str(e)
                    and attempt < max_retries - 1
                ):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Database not ready, retrying in {retry_delay}s..."
                        )
                    )
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 10)  # Exponential backoff
                    continue
                else:
                    # Re-raise if not connection issue or max retries reached
                    raise
