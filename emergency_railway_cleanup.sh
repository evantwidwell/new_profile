#!/bin/bash

# Emergency Railway Database Cleanup Script
# Run this when your Railway database is full and crashing

echo "🚨 EMERGENCY DATABASE CLEANUP FOR RAILWAY 🚨"
echo "This script will try to clean up your database even when it's nearly full"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install with: npm install -g @railway/cli"
    exit 1
fi

# Login to Railway (if not already)
echo "🔑 Logging into Railway..."
railway login

# Connect to database with minimal operations
echo "🗄️ Attempting emergency cleanup..."

# Method 1: Try to delete data in small batches
echo "Trying to delete data in small batches..."
railway run python manage.py shell -c "
import sys
from django.db import connection
from taxi_api.models import Trip

try:
    # Delete in very small batches to avoid memory issues
    batch_size = 1000
    deleted = 0
    
    while True:
        trips = Trip.objects.all()[:batch_size]
        if not trips:
            break
        
        trip_ids = [trip.id for trip in trips]
        Trip.objects.filter(id__in=trip_ids).delete()
        deleted += len(trip_ids)
        print(f'Deleted {deleted} records so far...')
        
        # Stop if we've deleted enough
        if deleted >= 10000:
            break
            
    print(f'Emergency cleanup completed. Deleted {deleted} records.')
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"

echo "✅ Emergency cleanup completed!"
echo ""
echo "Next steps:"
echo "1. Check Railway dashboard to see if space was freed"
echo "2. If still full, consider upgrading your plan"
echo "3. Run 'railway run python manage.py migrate' to ensure DB is healthy"
