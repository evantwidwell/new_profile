import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { LatLngBounds } from 'leaflet';
import type { HeatmapData } from '../services/api';
import { getZoneById, NYC_BOUNDS } from '../data/taxiZones';
import 'leaflet/dist/leaflet.css';

interface TaxiMapProps {
  heatmapData: HeatmapData[];
  selectedZone?: number;
  onZoneSelect: (zoneId: number) => void;
}

const MapBounds: React.FC<{ bounds: LatLngBounds }> = ({ bounds }) => {
  const map = useMap();
  
  useEffect(() => {
    map.fitBounds(bounds);
  }, [map, bounds]);
  
  return null;
};

const TaxiMap: React.FC<TaxiMapProps> = ({ 
  heatmapData, 
  selectedZone, 
  onZoneSelect 
}) => {
  // Create bounds for NYC
  const bounds = new LatLngBounds(
    [NYC_BOUNDS.bounds.south, NYC_BOUNDS.bounds.west],
    [NYC_BOUNDS.bounds.north, NYC_BOUNDS.bounds.east]
  );

  // Get max trip count for scaling circle sizes
  const maxTripCount = Math.max(...heatmapData.map(d => d.trip_count));
  const minTripCount = Math.min(...heatmapData.map(d => d.trip_count));

  // Scale circle radius based on trip count
  const getCircleRadius = (tripCount: number): number => {
    if (maxTripCount === minTripCount) return 8;
    const normalized = (tripCount - minTripCount) / (maxTripCount - minTripCount);
    return Math.max(4, Math.min(20, 4 + normalized * 16));
  };

  // Get color based on average fare
  const getCircleColor = (avgFare: number): string => {
    if (avgFare < 10) return '#3B82F6'; // Blue for low fare
    if (avgFare < 20) return '#10B981'; // Green for medium fare
    if (avgFare < 30) return '#F59E0B'; // Yellow for high fare
    return '#EF4444'; // Red for very high fare
  };

  // Get opacity based on selection
  const getCircleOpacity = (zoneId: number): number => {
    return selectedZone === undefined || selectedZone === zoneId ? 0.8 : 0.3;
  };

  return (
    <div className="w-full h-full">
      <MapContainer
        center={[NYC_BOUNDS.center.lat, NYC_BOUNDS.center.lng]}
        zoom={NYC_BOUNDS.zoom}
        className="w-full h-full"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        <MapBounds bounds={bounds} />
        
        {heatmapData.map((data) => {
          const zone = getZoneById(data.pickup_location_id);
          if (!zone) return null;
          
          return (
            <CircleMarker
              key={data.pickup_location_id}
              center={[zone.latitude, zone.longitude]}
              radius={getCircleRadius(data.trip_count)}
              color={getCircleColor(data.avg_fare)}
              fillColor={getCircleColor(data.avg_fare)}
              fillOpacity={getCircleOpacity(data.pickup_location_id)}
              stroke={selectedZone === data.pickup_location_id}
              weight={selectedZone === data.pickup_location_id ? 3 : 1}
              eventHandlers={{
                click: () => onZoneSelect(data.pickup_location_id),
              }}
            >
              <Popup>
                <div className="p-2 text-sm">
                  <h3 className="font-bold text-lg mb-2">{zone.zone}</h3>
                  <p className="text-gray-600 mb-2">{zone.borough}</p>
                  <div className="space-y-1">
                    <p><strong>Trips:</strong> {data.trip_count.toLocaleString()}</p>
                    <p><strong>Avg Fare:</strong> ${data.avg_fare.toFixed(2)}</p>
                    <p><strong>Avg Distance:</strong> {data.avg_distance.toFixed(2)} mi</p>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg z-[1000]">
        <h4 className="font-semibold mb-2">Trip Volume & Fare</h4>
        <div className="space-y-1 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-blue-500"></div>
            <span>Low Fare (&lt;$10)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>Medium Fare ($10-20)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span>High Fare ($20-30)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span>Very High Fare (&gt;$30)</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t">
          <p className="text-xs text-gray-600">Circle size = Trip volume</p>
        </div>
      </div>
    </div>
  );
};

export default TaxiMap;
