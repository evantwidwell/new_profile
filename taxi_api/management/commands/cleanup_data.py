from django.core.management.base import BaseCommand
from django.db import connection, transaction

from taxi_api.models import Trip, Zone


class Command(BaseCommand):
    help = "Clean up database data to free space"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-records",
            type=int,
            default=0,
            help="Number of most recent records to keep (default: 0)",
        )
        parser.add_argument(
            "--older-than-days", type=int, help="Delete records older than N days"
        )
        parser.add_argument(
            "--vacuum",
            action="store_true",
            help="Run VACUUM after cleanup to reclaim space",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        keep_records = options["keep_records"]
        older_than_days = options["older_than_days"]
        vacuum = options["vacuum"]

        # Get initial counts
        initial_trips = Trip.objects.count()
        initial_zones = Zone.objects.count()

        self.stdout.write("Initial counts:")
        self.stdout.write(f"  Trips: {initial_trips:,}")
        self.stdout.write(f"  Zones: {initial_zones:,}")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No data will be deleted"))

        # Build deletion query
        trips_to_delete = Trip.objects.all()

        if keep_records > 0:
            # Keep the most recent records
            trips_to_delete = trips_to_delete.order_by("-pickup_datetime")[
                keep_records:
            ]
            self.stdout.write(f"Will keep {keep_records} most recent records")

        if older_than_days:
            from datetime import datetime, timedelta

            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            trips_to_delete = trips_to_delete.filter(pickup_datetime__lt=cutoff_date)
            self.stdout.write(f"Will delete records older than {older_than_days} days")

        records_to_delete = trips_to_delete.count()
        self.stdout.write(f"Records to delete: {records_to_delete:,}")

        if records_to_delete == 0:
            self.stdout.write(self.style.SUCCESS("No records to delete"))
            return

        if not dry_run:
            # Confirm deletion
            if records_to_delete > 0:
                confirm = input(f"Delete {records_to_delete:,} records? (y/N): ")
                if confirm.lower() != "y":
                    self.stdout.write("Cancelled")
                    return

            # Delete in batches to avoid memory issues
            batch_size = 10000
            deleted_count = 0

            with transaction.atomic():
                while trips_to_delete.exists():
                    batch = trips_to_delete[:batch_size]
                    batch_ids = list(batch.values_list("id", flat=True))
                    Trip.objects.filter(id__in=batch_ids).delete()
                    deleted_count += len(batch_ids)
                    self.stdout.write(f"Deleted {deleted_count:,} records...")

            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted_count:,} trip records")
            )

            # Run vacuum if requested
            if vacuum:
                self.stdout.write("Running VACUUM to reclaim space...")
                with connection.cursor() as cursor:
                    cursor.execute("VACUUM FULL;")
                self.stdout.write(self.style.SUCCESS("VACUUM completed"))

        # Show final counts
        final_trips = Trip.objects.count()
        final_zones = Zone.objects.count()

        self.stdout.write("\nFinal counts:")
        self.stdout.write(f"  Trips: {final_trips:,}")
        self.stdout.write(f"  Zones: {final_zones:,}")
        self.stdout.write(f"  Records deleted: {initial_trips - final_trips:,}")
