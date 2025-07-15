import { useState, useEffect } from 'react';
import TaxiMap from './components/TaxiMap';
import StatsDashboard from './components/StatsDashboard';
import DatePicker from './components/DatePicker';
import { taxiApiService } from './services/api';
import type { 
  TripSummary, 
  TripStats, 
  RevenueAnalytics, 
  HeatmapData, 
  DataStatus 
} from './services/api';

function App() {
  const [dataStatus, setDataStatus] = useState<DataStatus | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(2024);
  const [selectedMonth, setSelectedMonth] = useState<number>(1);
  const [selectedZone, setSelectedZone] = useState<number | undefined>();
  const [activeTab, setActiveTab] = useState<'map' | 'stats'>('map');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [tripSummary, setTripSummary] = useState<TripSummary[]>([]);
  const [tripStats, setTripStats] = useState<TripStats | null>(null);
  const [revenueAnalytics, setRevenueAnalytics] = useState<RevenueAnalytics | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);

  // Load initial data status
  useEffect(() => {
    const loadDataStatus = async () => {
      try {
        const status = await taxiApiService.getDataStatus();
        setDataStatus(status);
        
        // Set default to latest available data
        if (status.available_data.length > 0) {
          const latest = status.available_data[status.available_data.length - 1];
          setSelectedYear(latest.year);
          setSelectedMonth(latest.month);
        }
      } catch (err) {
        setError('Failed to load data status');
        console.error('Error loading data status:', err);
      }
    };

    loadDataStatus();
  }, []);

  // Load data when date changes
  useEffect(() => {
    if (dataStatus && selectedYear && selectedMonth) {
      loadData();
    }
  }, [selectedYear, selectedMonth, dataStatus]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [summary, stats, analytics, heatmap] = await Promise.all([
        taxiApiService.getTripSummary(selectedYear, selectedMonth),
        taxiApiService.getTripStats(selectedYear, selectedMonth),
        taxiApiService.getRevenueAnalytics(selectedYear, selectedMonth),
        taxiApiService.getHeatmapData(selectedYear, selectedMonth)
      ]);

      setTripSummary(summary.data);
      setTripStats(stats.data);
      setRevenueAnalytics(analytics.data);
      setHeatmapData(heatmap.data);
    } catch (err) {
      setError('Failed to load taxi data');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (year: number, month: number) => {
    setSelectedYear(year);
    setSelectedMonth(month);
    setSelectedZone(undefined); // Reset zone selection
  };

  const handleZoneSelect = (zoneId: number) => {
    setSelectedZone(selectedZone === zoneId ? undefined : zoneId);
  };

  if (!dataStatus) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading NYC Taxi Data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">NYC Taxi Data Visualization</h1>
              <p className="mt-1 text-sm text-gray-600">
                Explore NYC taxi trip patterns and analytics
              </p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => setActiveTab('map')}
                className={`px-4 py-2 rounded-md font-medium ${
                  activeTab === 'map'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Map View
              </button>
              <button
                onClick={() => setActiveTab('stats')}
                className={`px-4 py-2 rounded-md font-medium ${
                  activeTab === 'stats'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Statistics
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Date Picker */}
        <div className="mb-6">
          <DatePicker
            selectedYear={selectedYear}
            selectedMonth={selectedMonth}
            onDateChange={handleDateChange}
            availableData={dataStatus.available_data}
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <div className="text-red-600">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <p className="ml-3 text-sm text-blue-700">Loading data...</p>
            </div>
          </div>
        )}

        {/* Content */}
        {activeTab === 'map' && (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="h-96 lg:h-[600px]">
              <TaxiMap
                heatmapData={heatmapData}
                selectedZone={selectedZone}
                onZoneSelect={handleZoneSelect}
              />
            </div>
          </div>
        )}

        {activeTab === 'stats' && (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <StatsDashboard
              tripSummary={tripSummary}
              tripStats={tripStats}
              revenueAnalytics={revenueAnalytics}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-600">
            Data powered by NYC Taxi & Limousine Commission • Built with React & DuckDB
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
