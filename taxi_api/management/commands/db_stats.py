from django.core.management.base import BaseCommand
from django.db import connection
from taxi_api.models import Trip, Zone


class Command(BaseCommand):
    help = 'Show database statistics and usage'

    def handle(self, *args, **options):
        # Get record counts
        trip_count = Trip.objects.count()
        zone_count = Zone.objects.count()
        
        self.stdout.write(self.style.SUCCESS('Database Statistics:'))
        self.stdout.write(f'  Trips: {trip_count:,}')
        self.stdout.write(f'  Zones: {zone_count:,}')
        
        # Get table sizes (PostgreSQL specific)
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    SELECT
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(
                            schemaname||'.'||tablename)) as size
                    FROM pg_tables
                    WHERE schemaname NOT IN (
                        'information_schema', 'pg_catalog')
                    ORDER BY pg_total_relation_size(
                        schemaname||'.'||tablename) DESC;
                """)
                
                self.stdout.write('\nTable Sizes:')
                for row in cursor.fetchall():
                    schema, table, size = row
                    self.stdout.write(f'  {schema}.{table}: {size}')
                
                # Get database size
                cursor.execute(
                    "SELECT pg_size_pretty(pg_database_size("
                    "current_database()));"
                )
                db_size = cursor.fetchone()[0]
                self.stdout.write(f'\nTotal Database Size: {db_size}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not get size info: {e}')
                )
                self.stdout.write(
                    'This is normal for SQLite or if you lack permissions'
                )
