import axios from 'axios';

const API_BASE_URL = '/api';

export interface TripSummary {
  date: string;
  total_trips: number;
  total_revenue: number;
  avg_fare: number;
  avg_distance: number;
  avg_tip: number;
  avg_passengers: number;
}

export interface TripStats {
  total_trips: number;
  total_revenue: number;
  avg_fare: number;
  avg_distance: number;
  avg_tip: number;
  earliest_trip: string;
  latest_trip: string;
  unique_pickup_locations: number;
  unique_dropoff_locations: number;
}

export interface HeatmapData {
  pickup_location_id: number;
  trip_count: number;
  avg_fare: number;
  avg_distance: number;
}

export interface RevenueAnalytics {
  hourly: Array<{
    hour: number;
    trips: number;
    revenue: number;
    avg_fare: number;
  }>;
  daily: Array<{
    day: number;
    trips: number;
    revenue: number;
    avg_fare: number;
  }>;
}

export interface Trip {
  pickup_datetime: string;
  dropoff_datetime: string;
  passenger_count: number;
  trip_distance: number;
  pickup_location_id: number;
  dropoff_location_id: number;
  fare_amount: number;
  tip_amount: number;
  total_amount: number;
}

export interface DataStatus {
  available_data: Array<{
    year: number;
    month: number;
    url: string;
  }>;
  message: string;
}

class TaxiApiService {
  private apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
  });

  async getDataStatus(): Promise<DataStatus> {
    const response = await this.apiClient.get('/taxi-data/status/');
    return response.data;
  }

  async getTripSummary(year: number, month: number): Promise<{ year: number; month: number; data: TripSummary[] }> {
    const response = await this.apiClient.get(`/taxi-data/summary/?year=${year}&month=${month}`);
    return response.data;
  }

  async getTripStats(year: number, month: number): Promise<{ year: number; month: number; data: TripStats }> {
    const response = await this.apiClient.get(`/taxi-data/stats/?year=${year}&month=${month}`);
    return response.data;
  }

  async getHeatmapData(year: number, month: number): Promise<{ year: number; month: number; data: HeatmapData[] }> {
    const response = await this.apiClient.get(`/taxi-data/heatmap/?year=${year}&month=${month}`);
    return response.data;
  }

  async getRevenueAnalytics(year: number, month: number): Promise<{ year: number; month: number; data: RevenueAnalytics }> {
    const response = await this.apiClient.get(`/taxi-data/revenue/?year=${year}&month=${month}`);
    return response.data;
  }

  async getSampleTrips(year: number, month: number, limit: number = 100): Promise<{ year: number; month: number; count: number; data: Trip[] }> {
    const response = await this.apiClient.get(`/taxi-data/trips/?year=${year}&month=${month}&limit=${limit}`);
    return response.data;
  }
}

export const taxiApiService = new TaxiApiService();
