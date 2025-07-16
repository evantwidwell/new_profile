import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import type { HeatmapData } from '../services/api';
import { getZoneById } from '../data/taxiZones';
import 'leaflet/dist/leaflet.css';

interface TaxiMapProps {
  heatmapData: HeatmapData[];
  selectedZone?: number;
  onZoneSelect: (zoneId: number) => void;
}

const TaxiMap: React.FC<TaxiMapProps> = ({ 
  heatmapData, 
  selectedZone, 
  onZoneSelect 
}) => {
  // Debug logging
  console.log('TaxiMap received heatmapData:', heatmapData);
  console.log('Number of data points:', heatmapData.length);
  console.log('Selected zone:', selectedZone);
  
  // Simple map with fixed height and basic styling
  return (
    <div style={{ height: '70vh', minHeight: '500px', width: '100%', position: 'relative' }}>
      <MapContainer
        center={[40.7589, -73.9851]}
        zoom={11}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {/* Test marker to verify map is working */}
        <CircleMarker
          center={[40.7589, -73.9851]}
          radius={10}
          color="red"
          fillColor="red"
          fillOpacity={0.8}
        >
          <Popup>Test marker - Manhattan center</Popup>
        </CircleMarker>
        
        {/* Render actual data markers */}
        {heatmapData.map((data) => {
          const zone = getZoneById(data.pickup_location_id);
          console.log(`Processing zone ${data.pickup_location_id}:`, zone);
          
          if (!zone) {
            console.warn(`Zone ${data.pickup_location_id} not found`);
            return null;
          }
          
          console.log(`Rendering CircleMarker for zone ${data.pickup_location_id} at [${zone.latitude}, ${zone.longitude}]`);
          
          return (
            <CircleMarker
              key={data.pickup_location_id}
              center={[zone.latitude, zone.longitude]}
              radius={Math.max(5, Math.min(20, data.trip_count / 10000))}
              color={data.avg_fare > 20 ? 'red' : 'blue'}
              fillColor={data.avg_fare > 20 ? 'red' : 'blue'}
              fillOpacity={0.6}
              eventHandlers={{
                click: () => onZoneSelect(data.pickup_location_id),
              }}
            >
              <Popup>
                <div>
                  <h3>{zone.zone}</h3>
                  <p>{zone.borough}</p>
                  <p><strong>Trips:</strong> {data.trip_count.toLocaleString()}</p>
                  <p><strong>Avg Fare:</strong> ${data.avg_fare.toFixed(2)}</p>
                  <p><strong>Avg Distance:</strong> {data.avg_distance.toFixed(2)} mi</p>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
      
      {/* Legend */}
      <div style={{ 
        position: 'absolute', 
        bottom: '10px', 
        left: '10px', 
        background: 'white', 
        padding: '12px', 
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
        zIndex: 1000,
        minWidth: '200px',
        color: '#333'
      }}>
        <h4 style={{ margin: '0 0 12px 0', fontWeight: 'bold', fontSize: '14px', color: '#333' }}>NYC Taxi Trip Data</h4>
        
        <div style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '6px', color: '#333' }}>Average Fare Range:</div>
          <div style={{ fontSize: '11px' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'blue', marginRight: '8px' }}></div>
              <span style={{ color: '#333' }}>Low Fare (&lt; $20)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'red', marginRight: '8px' }}></div>
              <span style={{ color: '#333' }}>High Fare (≥ $20)</span>
            </div>
          </div>
        </div>
        
        <div style={{ marginBottom: '8px' }}>
          <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '6px', color: '#333' }}>Circle Size:</div>
          <div style={{ fontSize: '11px' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '3px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#666', marginRight: '8px' }}></div>
              <span style={{ color: '#333' }}>Small: &lt;50K trips</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '3px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#666', marginRight: '8px' }}></div>
              <span style={{ color: '#333' }}>Medium: 50K-150K trips</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '16px', height: '16px', borderRadius: '50%', backgroundColor: '#666', marginRight: '8px' }}></div>
              <span style={{ color: '#333' }}>Large: &gt;150K trips</span>
            </div>
          </div>
        </div>
        
        <div style={{ paddingTop: '8px', borderTop: '1px solid #eee' }}>
          <p style={{ margin: 0, fontSize: '10px', color: '#666', fontStyle: 'italic' }}>
            Click markers for details • Data from NYC TLC
          </p>
        </div>
      </div>
    </div>
  );
};

export default TaxiMap;
