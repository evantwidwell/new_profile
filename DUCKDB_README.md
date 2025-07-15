# NYC Taxi Data API - DuckDB Direct Querying

## 🎉 No More Database Storage Issues!

This new approach uses **DuckDB** to query NYC Taxi data directly from parquet files, eliminating the need to store millions of records in PostgreSQL.

## How It Works

1. **Direct Parquet Querying**: DuckDB queries parquet files directly from NYC's data URLs
2. **No Database Storage**: No need to load data into PostgreSQL
3. **On-Demand Analytics**: Data is processed when requested
4. **Memory Efficient**: Uses DuckDB's efficient columnar processing

## New API Endpoints

### DuckDB-Based Endpoints (Recommended)
- `GET /api/taxi-data/status/` - Check available data
- `GET /api/taxi-data/summary/?year=2023&month=1` - Daily trip summaries
- `GET /api/taxi-data/stats/?year=2023&month=1` - Trip statistics
- `GET /api/taxi-data/trips/?year=2023&month=1&limit=100` - Sample trips
- `GET /api/taxi-data/heatmap/?year=2023&month=1` - Heatmap data
- `GET /api/taxi-data/revenue/?year=2023&month=1` - Revenue analytics

### Query Parameters
- `year`: Year to query (default: 2023)
- `month`: Month to query (default: 1)
- `limit`: Number of records to return (varies by endpoint)

## Usage Examples

```bash
# Get trip summary for January 2023
curl "http://localhost:8000/api/taxi-data/summary/?year=2023&month=1"

# Get trip statistics
curl "http://localhost:8000/api/taxi-data/stats/?year=2023&month=1"

# Get sample trips
curl "http://localhost:8000/api/taxi-data/trips/?year=2023&month=1&limit=10"
```

## Make Commands

```bash
# Test DuckDB endpoints
make api-test-duckdb

# Test all endpoints
make api-test

# Start the app
make up
```

## Benefits

1. **No Storage Limits**: No more database disk space issues
2. **Always Fresh Data**: Queries the latest data from NYC's servers
3. **Faster Development**: No need to load data before testing
4. **Cost Effective**: No database storage costs on Railway
5. **Scalable**: Handles any amount of data without storage constraints

## Performance

- First query per month may take a few seconds (downloading parquet file)
- Subsequent queries are fast due to DuckDB's efficient processing
- Memory usage is minimal compared to loading into PostgreSQL

## Migration from PostgreSQL

The old PostgreSQL-based endpoints are still available but deprecated:
- `GET /api/trips/` (old)
- `GET /api/trips/summary/` (old)

New applications should use the DuckDB endpoints (`/api/taxi-data/...`).
