import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import type { TripSummary, TripStats, RevenueAnalytics } from '../services/api';
import { format } from 'date-fns';

interface StatsDashboardProps {
  tripSummary: TripSummary[];
  tripStats: TripStats | null;
  revenueAnalytics: RevenueAnalytics | null;
}

const StatsDashboard: React.FC<StatsDashboardProps> = ({
  tripSummary,
  tripStats,
  revenueAnalytics
}) => {
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  // Format data for charts
  const dailyTripData = tripSummary.map(item => ({
    date: format(new Date(item.date), 'MM/dd'),
    trips: item.total_trips,
    revenue: item.total_revenue,
    avgFare: item.avg_fare,
    avgDistance: item.avg_distance
  }));

  const hourlyData = revenueAnalytics?.hourly.map(item => ({
    hour: `${item.hour}:00`,
    trips: item.trips,
    revenue: item.revenue,
    avgFare: item.avg_fare
  })) || [];

  const dailyRevenueData = revenueAnalytics?.daily.map(item => ({
    day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][item.day],
    trips: item.trips,
    revenue: item.revenue,
    avgFare: item.avg_fare
  })) || [];

  return (
    <div className="p-6 space-y-6">
      {/* Key Metrics */}
      {tripStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-blue-600">Total Trips</h3>
            <p className="text-2xl font-bold text-blue-900">
              {tripStats.total_trips.toLocaleString()}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-green-600">Total Revenue</h3>
            <p className="text-2xl font-bold text-green-900">
              ${tripStats.total_revenue.toLocaleString()}
            </p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-yellow-600">Avg Fare</h3>
            <p className="text-2xl font-bold text-yellow-900">
              ${tripStats.avg_fare.toFixed(2)}
            </p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-purple-600">Avg Distance</h3>
            <p className="text-2xl font-bold text-purple-900">
              {tripStats.avg_distance.toFixed(2)} mi
            </p>
          </div>
        </div>
      )}

      {/* Daily Trip Trends */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Daily Trip Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyTripData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip 
              formatter={(value: number, name: string) => [
                name === 'trips' ? value.toLocaleString() : 
                name === 'revenue' ? `$${value.toLocaleString()}` :
                name === 'avgFare' ? `$${value.toFixed(2)}` :
                `${value.toFixed(2)} mi`,
                name === 'trips' ? 'Trips' :
                name === 'revenue' ? 'Revenue' :
                name === 'avgFare' ? 'Avg Fare' : 'Avg Distance'
              ]}
            />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="trips" stroke="#3B82F6" name="Trips" />
            <Line yAxisId="right" type="monotone" dataKey="avgFare" stroke="#10B981" name="Avg Fare" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Hourly Activity */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Hourly Activity Pattern</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={hourlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip 
              formatter={(value: number) => [value.toLocaleString(), 'Trips']}
            />
            <Bar dataKey="trips" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Day of Week Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Weekly Trip Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dailyRevenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [value.toLocaleString(), 'Trips']}
              />
              <Bar dataKey="trips" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Weekly Revenue Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={dailyRevenueData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ day, percent }) => `${day} ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="revenue"
              >
                {dailyRevenueData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => [`$${value.toLocaleString()}`, 'Revenue']}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Trip Details */}
      {tripStats && (
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Trip Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Average Tip</p>
              <p className="text-xl font-semibold">${tripStats.avg_tip.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Unique Pickup Locations</p>
              <p className="text-xl font-semibold">{tripStats.unique_pickup_locations}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Unique Dropoff Locations</p>
              <p className="text-xl font-semibold">{tripStats.unique_dropoff_locations}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Earliest Trip</p>
              <p className="text-xl font-semibold">
                {format(new Date(tripStats.earliest_trip), 'MM/dd/yyyy')}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Latest Trip</p>
              <p className="text-xl font-semibold">
                {format(new Date(tripStats.latest_trip), 'MM/dd/yyyy')}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsDashboard;
