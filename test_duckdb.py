#!/usr/bin/env python3
"""
Test script to verify DuckDB direct parquet querying works
This bypasses the Django setup for quick testing
"""

import sys
import os

# Add the parent directory to the path so we can import the service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taxi_api.services import TaxiDataService


def test_duckdb_service():
    """Test the DuckDB service with direct parquet queries"""
    print("🦆 Testing DuckDB direct parquet querying...")
    
    service = TaxiDataService()
    
    try:
        # Test 1: Get trip summary
        print("\n📊 Testing trip summary...")
        summary = service.get_trip_summary(2023, 1, limit=5)
        print(f"Found {len(summary)} days of data")
        if summary:
            print(f"Sample: {summary[0]}")
        
        # Test 2: Get trip stats
        print("\n📈 Testing trip statistics...")
        stats = service.get_trip_stats(2023, 1)
        print(f"Total trips: {stats.get('total_trips', 'N/A')}")
        print(f"Total revenue: ${stats.get('total_revenue', 'N/A')}")
        
        # Test 3: Get sample trips
        print("\n🚕 Testing sample trips...")
        trips = service.get_sample_trips(2023, 1, limit=3)
        print(f"Found {len(trips)} sample trips")
        if trips:
            print(f"Sample trip: {trips[0]}")
        
        # Test 4: Get heatmap data
        print("\n🗺️ Testing heatmap data...")
        heatmap = service.get_heatmap_data(2023, 1, limit=5)
        print(f"Found {len(heatmap)} location clusters")
        if heatmap:
            print(f"Top location: {heatmap[0]}")
            
        print("\n✅ All tests passed! DuckDB direct querying works!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        service.close()


if __name__ == "__main__":
    test_duckdb_service()
