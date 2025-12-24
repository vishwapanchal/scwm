'use client';

import { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import 'leaflet-routing-machine';

// --- STYLES ---
const markerStyles = `
  .leaflet-div-icon { background: transparent; border: none; }
  .user-dot-container { position: relative; display: flex; justify-content: center; align-items: center; }
  .user-dot { width: 14px; height: 14px; background: #3b82f6; border: 2px solid white; border-radius: 50%; z-index: 10; }
  .user-pulse { position: absolute; width: 30px; height: 30px; background: rgba(59, 130, 246, 0.4); border-radius: 50%; animation: pulse 2s infinite; }
  @keyframes pulse { 0% { transform: scale(0.5); opacity: 1; } 100% { transform: scale(2); opacity: 0; } }
  .glow-pin { filter: drop-shadow(0 0 10px #10b981) scale(1.3); }
`;

// --- HELPERS ---
const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
  const R = 6371; 
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
};

// --- MAP CONTROLS ---
function MapManager({ userPos, selectedCenter, routingTarget }: any) {
  const map = useMap();

  useEffect(() => {
    if (selectedCenter) {
      map.flyTo([selectedCenter.latitude, selectedCenter.longitude], 15);
    }
  }, [selectedCenter, map]);

  useEffect(() => {
    if (routingTarget && userPos) {
      // Clear previous routes manually if needed, or rely on React cleanup
      const control = L.Routing.control({
        waypoints: [L.latLng(userPos[0], userPos[1]), L.latLng(routingTarget[0], routingTarget[1])],
        routeWhileDragging: false,
        addWaypoints: false,
        show: false
      }).addTo(map);
      return () => { map.removeControl(control); };
    }
  }, [routingTarget, userPos, map]);

  return null;
}

export default function MapComponent({ centers }: { centers: any[] }) {
  const [userPos, setUserPos] = useState<[number, number] | null>(null);
  const [selectedCenter, setSelectedCenter] = useState<any>(null);
  const [routingTarget, setRoutingTarget] = useState<[number, number] | null>(null);

  // 1. Initial Location Request
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setUserPos([pos.coords.latitude, pos.coords.longitude]),
        (err) => console.error("Location blocked", err)
      );
    }
  }, []);

  // 2. Sort by Distance
  const sortedData = useMemo(() => {
    return centers.map(c => ({
      ...c,
      dist: userPos ? calculateDistance(userPos[0], userPos[1], c.latitude, c.longitude) : null
    })).sort((a, b) => (a.dist ?? 9999) - (b.dist ?? 9999));
  }, [centers, userPos]);

  return (
    <div className="flex flex-col md:flex-row gap-4 h-[650px] w-full text-white">
      <style jsx global>{markerStyles}</style>

      {/* SIDEBAR */}
      <div className="w-full md:w-1/3 bg-slate-900 rounded-xl p-4 overflow-y-auto border border-slate-800 custom-scrollbar">
        <h3 className="text-emerald-400 font-bold mb-4 flex justify-between items-center">
          Nearby Centers
          {userPos && <span className="text-[10px] text-slate-400">Sorted by distance</span>}
        </h3>
        <div className="space-y-2">
          {sortedData.map((c, i) => (
            <div 
              key={i} 
              onClick={() => { setSelectedCenter(c); setRoutingTarget([c.latitude, c.longitude]); }}
              className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedCenter?.name === c.name ? 'border-emerald-500 bg-emerald-500/10' : 'border-slate-700 bg-slate-800/50 hover:border-slate-500'}`}
            >
              <p className="font-bold text-sm">{c.name}</p>
              <p className="text-xs text-slate-400 mt-1">{c.dist ? `🚗 ${c.dist.toFixed(1)} km away` : 'Locating you...'}</p>
            </div>
          ))}
        </div>
      </div>

      {/* MAP AREA */}
      <div className="flex-1 relative rounded-xl overflow-hidden border border-slate-800">
        <MapContainer center={[12.9716, 77.5946]} zoom={12} style={{ height: "100%", width: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          
          <MapManager userPos={userPos} selectedCenter={selectedCenter} routingTarget={routingTarget} />

          {/* User Marker */}
          {userPos && (
            <Marker position={userPos} icon={L.divIcon({
              className: 'leaflet-div-icon',
              html: `<div class="user-dot-container"><div class="user-pulse"></div><div class="user-dot"></div></div>`
            })}>
              <Popup>You are here</Popup>
            </Marker>
          )}

          {/* Centers */}
          {centers.map((c, i) => (
            <Marker 
              key={i} 
              position={[c.latitude, c.longitude]} 
              icon={L.divIcon({
                className: 'leaflet-div-icon',
                html: `<div class="emoji-pin ${selectedCenter?.name === c.name ? 'glow-pin' : ''}">📍</div>`
              })}
              eventHandlers={{ click: () => { setSelectedCenter(c); setRoutingTarget([c.latitude, c.longitude]); }}}
            >
              <Popup>
                <div className="text-slate-900">
                  <b>{c.name}</b><br/>
                  <p className="text-xs my-1">{c.address}</p>
                  <a href={`https://www.google.com/maps/dir/?api=1&destination=${c.latitude},${c.longitude}`} target="_blank" className="text-blue-600 text-xs font-bold">Open in Google Maps ➔</a>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Recenter Button Overlay */}
        {userPos && (
          <button 
            onClick={() => setSelectedCenter({ latitude: userPos[0], longitude: userPos[1] })}
            className="absolute bottom-6 right-6 z-[1000] bg-white text-slate-900 p-3 rounded-full shadow-xl hover:bg-slate-100 transition-all"
            title="My Location"
          >
            🎯
          </button>
        )}
      </div>
    </div>
  );
}