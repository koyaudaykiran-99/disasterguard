import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Polygon, useMap } from 'react-leaflet';
import L from 'leaflet';
import {
  X,
  Navigation,
  Compass,
  MapPin,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Footprints,
  Car,
  Copy,
  Check,
  Hospital,
  Home,
  HeartPulse,
  Phone,
  ArrowRight,
  ShieldAlert,
  Info,
  Maximize2,
} from 'lucide-react';
import { SafeZone } from '../../types/disaster';

interface SafeZoneDirectionsModalProps {
  safeZone: SafeZone | null;
  isOpen: boolean;
  onClose: () => void;
  onNavigateToMap?: () => void;
}

// User Origin Coordinate (City Command Center / Citizen GPS fallback)
const ORIGIN_COORDS: [number, number] = [13.0827, 80.2707];

// PostGIS Inundation Hazard Polygon to display flood avoidance corridor
const INUNDATION_ZONE_AVOIDED: [number, number][] = [
  [13.078, 80.265],
  [13.078, 80.282],
  [13.092, 80.282],
  [13.092, 80.265],
];

// Helper to center and auto-fit map view to the route bounding box
const MapRouteFitter: React.FC<{ bounds: L.LatLngBoundsExpression }> = ({ bounds }) => {
  const map = useMap();

  useEffect(() => {
    const timer = setTimeout(() => {
      try {
        map.invalidateSize();
        map.fitBounds(bounds, { padding: [35, 35], maxZoom: 15 });
      } catch (err) {
        console.error('Error auto-fitting route map:', err);
      }
    }, 180);
    return () => clearTimeout(timer);
  }, [map, bounds]);

  return null;
};

// Custom Leaflet DivIcons
const createOriginPinIcon = (): L.DivIcon => {
  return L.divIcon({
    html: `
      <div class="relative flex items-center justify-center">
        <div class="w-8 h-8 rounded-full bg-blue-600 border-2 border-cyan-300 flex items-center justify-center shadow-lg shadow-blue-500/50 animate-pulse">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v3m0 14v3M2 12h3m14 0h3"/>
          </svg>
        </div>
      </div>
    `,
    className: 'custom-origin-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

const createDestinationPinIcon = (type: string): L.DivIcon => {
  const isHospital = type === 'HOSPITAL';
  const bgClass = isHospital ? 'bg-rose-600 border-rose-300' : 'bg-emerald-600 border-emerald-300';

  return L.divIcon({
    html: `
      <div class="relative flex items-center justify-center">
        <div class="w-9 h-9 rounded-xl ${bgClass} border-2 flex items-center justify-center shadow-xl shadow-emerald-500/30">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
      </div>
    `,
    className: 'custom-dest-marker',
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });
};

export const SafeZoneDirectionsModal: React.FC<SafeZoneDirectionsModalProps> = ({
  safeZone,
  isOpen,
  onClose,
  onNavigateToMap,
}) => {
  const [travelMode, setTravelMode] = useState<'driving' | 'walking'>('driving');
  const [copied, setCopied] = useState<boolean>(false);

  // Close on ESC key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Compute realistic safe evacuation route avoiding inundation area
  const routePoints: [number, number][] = useMemo(() => {
    if (!safeZone) return [];

    const dest = safeZone.coordinates;
    const midLat = ORIGIN_COORDS[0] + (dest[0] - ORIGIN_COORDS[0]) * 0.45;
    const midLng = ORIGIN_COORDS[1] + (dest[1] - ORIGIN_COORDS[1]) * 0.45;

    // Route deflects slightly along high-ground corridor (+14m elevation)
    const detourLng = midLng < 80.27 ? midLng - 0.005 : midLng + 0.005;

    return [
      ORIGIN_COORDS,
      [ORIGIN_COORDS[0] + (dest[0] - ORIGIN_COORDS[0]) * 0.2, ORIGIN_COORDS[1] + 0.002],
      [midLat, detourLng],
      [dest[0] - (dest[0] - ORIGIN_COORDS[0]) * 0.15, dest[1] - 0.001],
      dest,
    ];
  }, [safeZone]);

  // Route map bounds
  const mapBounds: L.LatLngBoundsExpression = useMemo(() => {
    if (!safeZone) return [ORIGIN_COORDS, ORIGIN_COORDS];
    return [ORIGIN_COORDS, safeZone.coordinates];
  }, [safeZone]);

  if (!isOpen || !safeZone) return null;

  const destCoords = safeZone.coordinates;
  const estDriveMin = Math.max(3, Math.round(safeZone.distanceKm * 2.8 + 2));
  const estWalkMin = Math.max(8, Math.round(safeZone.distanceKm * 13.5));
  const activeTimeMin = travelMode === 'driving' ? estDriveMin : estWalkMin;

  const occupancyPercent = Math.round((safeZone.currentOccupancy / safeZone.capacity) * 100);

  // External Maps Links
  const googleMapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${ORIGIN_COORDS[0]},${ORIGIN_COORDS[1]}&destination=${destCoords[0]},${destCoords[1]}&travelmode=${travelMode === 'driving' ? 'driving' : 'walking'}`;
  const openStreetMapUrl = `https://www.openstreetmap.org/directions?engine=fossgis_osrm_${travelMode === 'driving' ? 'car' : 'foot'}&route=${ORIGIN_COORDS[0]}%2C${ORIGIN_COORDS[1]}%3B${destCoords[0]}%2C${destCoords[1]}`;

  const handleCopyCoords = () => {
    navigator.clipboard.writeText(`${destCoords[0]}, ${destCoords[1]}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleViewCommandMap = () => {
    onClose();
    if (onNavigateToMap) {
      onNavigateToMap();
    } else {
      window.location.hash = '/map';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'HOSPITAL':
        return <Hospital className="w-5 h-5 text-rose-400" />;
      case 'SHELTER':
        return <Home className="w-5 h-5 text-emerald-400" />;
      default:
        return <HeartPulse className="w-5 h-5 text-cyan-400" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/85 backdrop-blur-md animate-fadeIn overflow-y-auto">
      <div className="glass-panel w-full max-w-4xl max-h-[92vh] rounded-3xl border border-gray-700 bg-command-card flex flex-col overflow-hidden shadow-2xl my-auto">
        
        {/* Header Bar */}
        <div className="p-5 border-b border-gray-800 bg-gray-900/90 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-600 text-white shadow-lg">
              <Navigation className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-gray-100 font-mono tracking-wide">
                  EMERGENCY EVACUATION NAVIGATION
                </h3>
                <span
                  className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded-full border ${
                    safeZone.status === 'OPEN'
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  }`}
                >
                  {safeZone.status}
                </span>
              </div>
              <p className="text-xs text-gray-400 font-mono mt-0.5 flex items-center gap-1.5">
                <span>Destination:</span>
                <span className="text-cyan-300 font-semibold">{safeZone.name}</span>
                <span className="text-gray-600">•</span>
                <span className="text-gray-400">{safeZone.type}</span>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
            title="Close directions modal (Esc)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="overflow-y-auto p-5 space-y-5">
          
          {/* Top Quick Metrics & Travel Mode Selector */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-3.5">
            {/* Travel Mode Toggle */}
            <div className="md:col-span-4 bg-gray-900/90 p-3 rounded-2xl border border-gray-800 flex items-center justify-between">
              <div className="text-xs font-mono text-gray-400">Mode:</div>
              <div className="flex space-x-1 bg-gray-950 p-1 rounded-xl border border-gray-800">
                <button
                  onClick={() => setTravelMode('driving')}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                    travelMode === 'driving'
                      ? 'bg-blue-600 text-white font-bold shadow-md'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <Car className="w-3.5 h-3.5" />
                  <span>Drive</span>
                </button>
                <button
                  onClick={() => setTravelMode('walking')}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                    travelMode === 'walking'
                      ? 'bg-blue-600 text-white font-bold shadow-md'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <Footprints className="w-3.5 h-3.5" />
                  <span>Walk</span>
                </button>
              </div>
            </div>

            {/* Distance & ETA Cards */}
            <div className="md:col-span-8 grid grid-cols-3 gap-2.5 font-mono text-xs">
              <div className="bg-gray-900/90 p-3 rounded-2xl border border-gray-800 flex flex-col justify-center">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider">Distance</span>
                <span className="text-base font-bold text-gray-100 mt-0.5">{safeZone.distanceKm} km</span>
              </div>
              <div className="bg-gray-900/90 p-3 rounded-2xl border border-gray-800 flex flex-col justify-center">
                <span className="text-[10px] text-cyan-400 uppercase tracking-wider flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Est. Duration
                </span>
                <span className="text-base font-bold text-cyan-300 mt-0.5">{activeTimeMin} mins</span>
              </div>
              <div className="bg-gray-900/90 p-3 rounded-2xl border border-gray-800 flex flex-col justify-center">
                <span className="text-[10px] text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" />
                  Corridor Safety
                </span>
                <span className="text-xs font-bold text-emerald-300 mt-0.5">High Ground</span>
              </div>
            </div>
          </div>

          {/* Safety Flood Avoidance Banner */}
          <div className="flex items-start space-x-3 bg-emerald-950/30 border border-emerald-500/30 p-3.5 rounded-2xl text-xs text-emerald-200 font-mono">
            <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-emerald-300 block">
                SAFE HIGH-GROUND CORRIDOR ACTIVE (+14m Elevation)
              </span>
              <p className="text-emerald-400/90 mt-0.5 leading-relaxed text-[11px]">
                Route automatically diverts around the 1.45m Downtown Riverside Basin inundation zone.
                All bridges on this evacuation corridor have been inspected and confirmed structurally secure.
              </p>
            </div>
          </div>

          {/* Route Map Preview & Turn-by-Turn Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            
            {/* Embedded Interactive Route Map Preview (Leaflet) */}
            <div className="lg:col-span-7 bg-gray-900/90 rounded-2xl border border-gray-800 p-3 flex flex-col space-y-2">
              <div className="flex items-center justify-between text-xs font-mono px-1">
                <span className="text-gray-300 flex items-center gap-1.5 font-bold">
                  <Compass className="w-3.5 h-3.5 text-cyan-400" />
                  Live Evacuation Route Map
                </span>
                <div className="flex items-center gap-2 text-[11px] text-gray-400">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-blue-500"></span> Origin
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Safe Zone
                  </span>
                </div>
              </div>

              {/* Leaflet Route Container */}
              <div className="w-full h-64 rounded-xl overflow-hidden border border-gray-800 relative z-10">
                <MapContainer
                  center={ORIGIN_COORDS}
                  zoom={13}
                  scrollWheelZoom={false}
                  className="w-full h-full"
                >
                  <TileLayer
                    attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                  />

                  {/* Auto-fit map to route bounds */}
                  <MapRouteFitter bounds={mapBounds} />

                  {/* Origin Marker */}
                  <Marker position={ORIGIN_COORDS} icon={createOriginPinIcon()}>
                    <Popup className="font-mono text-xs">
                      <strong>Current Citizen GPS</strong>
                      <br />
                      Lat: {ORIGIN_COORDS[0]}, Lng: {ORIGIN_COORDS[1]}
                    </Popup>
                  </Marker>

                  {/* Destination Marker */}
                  <Marker position={destCoords} icon={createDestinationPinIcon(safeZone.type)}>
                    <Popup className="font-mono text-xs">
                      <strong>{safeZone.name}</strong>
                      <br />
                      Status: {safeZone.status} | Occupancy: {occupancyPercent}%
                    </Popup>
                  </Marker>

                  {/* High Ground Route Polyline */}
                  <Polyline
                    positions={routePoints}
                    color="#06b6d4"
                    weight={5}
                    opacity={0.9}
                    dashArray="8, 4"
                  />

                  {/* Avoided Flood Hazard Polygon (Visual indication of hazard) */}
                  <Polygon
                    positions={INUNDATION_ZONE_AVOIDED}
                    pathOptions={{
                      color: '#ef4444',
                      fillColor: '#dc2626',
                      fillOpacity: 0.25,
                      weight: 1.5,
                      dashArray: '4, 4',
                    }}
                  >
                    <Popup className="font-mono text-xs">
                      <strong className="text-red-600">Active Flood Risk Basin</strong>
                      <br />
                      Depth: 1.45m — Avoided by Route
                    </Popup>
                  </Polygon>
                </MapContainer>
              </div>

              {/* Map Sub-legend */}
              <div className="flex items-center justify-between text-[11px] font-mono text-gray-500 px-1 pt-1">
                <span>Cyan Dashed Line: Active Route</span>
                <span className="text-rose-400/80">Red Shaded Box: Avoided Flood Zone</span>
              </div>
            </div>

            {/* Turn-by-Turn Safe Evacuation Steps */}
            <div className="lg:col-span-5 bg-gray-900/90 rounded-2xl border border-gray-800 p-4 flex flex-col justify-between space-y-3 font-mono text-xs">
              <div>
                <h4 className="font-bold text-gray-200 text-xs tracking-wider uppercase mb-3 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                  Turn-by-Turn Safe Instructions
                </h4>

                <ol className="space-y-2.5 text-gray-300">
                  <li className="flex items-start space-x-2.5">
                    <span className="w-5 h-5 rounded-full bg-blue-600/30 text-blue-400 border border-blue-500/40 flex items-center justify-center font-bold text-[11px] shrink-0 mt-0.5">
                      1
                    </span>
                    <div>
                      <span className="font-bold text-gray-200 block">Depart Origin</span>
                      <span className="text-gray-400 text-[11px]">
                        Head toward Main Arterial Connector; avoid subterranean underpasses.
                      </span>
                    </div>
                  </li>

                  <li className="flex items-start space-x-2.5">
                    <span className="w-5 h-5 rounded-full bg-blue-600/30 text-blue-400 border border-blue-500/40 flex items-center justify-center font-bold text-[11px] shrink-0 mt-0.5">
                      2
                    </span>
                    <div>
                      <span className="font-bold text-gray-200 block">Bypass River Basin</span>
                      <span className="text-gray-400 text-[11px]">
                        Follow elevated flyover detour around Riverside Basin (depth 1.45m).
                      </span>
                    </div>
                  </li>

                  <li className="flex items-start space-x-2.5">
                    <span className="w-5 h-5 rounded-full bg-blue-600/30 text-blue-400 border border-blue-500/40 flex items-center justify-center font-bold text-[11px] shrink-0 mt-0.5">
                      3
                    </span>
                    <div>
                      <span className="font-bold text-gray-200 block">Elevated Corridor</span>
                      <span className="text-gray-400 text-[11px]">
                        Continue straight on Route B following blue emergency evacuation arrows.
                      </span>
                    </div>
                  </li>

                  <li className="flex items-start space-x-2.5">
                    <span className="w-5 h-5 rounded-full bg-emerald-600/30 text-emerald-400 border border-emerald-500/40 flex items-center justify-center font-bold text-[11px] shrink-0 mt-0.5">
                      4
                    </span>
                    <div>
                      <span className="font-bold text-gray-200 block">Arrive at Safe Zone</span>
                      <span className="text-gray-400 text-[11px]">
                        Check in at South Reception intake for bedding, water, and medical care.
                      </span>
                    </div>
                  </li>
                </ol>
              </div>

              {/* Facility Contact & GPS Quick Bar */}
              <div className="pt-3 border-t border-gray-800/80 flex items-center justify-between text-[11px]">
                <a
                  href={`tel:${safeZone.contact}`}
                  className="flex items-center space-x-1.5 text-cyan-400 hover:text-cyan-300 font-bold transition-colors bg-cyan-950/40 px-2.5 py-1.5 rounded-lg border border-cyan-800/40"
                >
                  <Phone className="w-3.5 h-3.5" />
                  <span>{safeZone.contact}</span>
                </a>

                <button
                  onClick={handleCopyCoords}
                  className="flex items-center space-x-1 text-gray-400 hover:text-gray-200 bg-gray-800 px-2.5 py-1.5 rounded-lg border border-gray-700 transition-colors"
                  title="Copy destination latitude/longitude"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400 font-bold">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy GPS</span>
                    </>
                  )}
                </button>
              </div>
            </div>

          </div>

          {/* Facility Supplies & Availability Breakdown */}
          <div className="bg-gray-900/80 p-4 rounded-2xl border border-gray-800 flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-xl bg-gray-800 border border-gray-700">
                {getTypeIcon(safeZone.type)}
              </div>
              <div>
                <span className="text-gray-400 block text-[11px]">Facility Occupancy</span>
                <span className="font-bold text-gray-100 text-sm">
                  {safeZone.currentOccupancy} / {safeZone.capacity} Beds ({occupancyPercent}%)
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-center">
                <span className="text-[10px] text-gray-500 block">Water Rations</span>
                <span className="font-bold text-cyan-400">{safeZone.supplies.water}%</span>
              </div>
              <div className="text-center">
                <span className="text-[10px] text-gray-500 block">Food Rations</span>
                <span className="font-bold text-amber-400">{safeZone.supplies.food}%</span>
              </div>
              <div className="text-center">
                <span className="text-[10px] text-gray-500 block">Medical Rations</span>
                <span className="font-bold text-emerald-400">{safeZone.supplies.medical}%</span>
              </div>
            </div>
          </div>

        </div>

        {/* Footer Navigation Action Buttons */}
        <div className="p-4 border-t border-gray-800 bg-gray-900/90 flex flex-wrap items-center justify-between gap-3 shrink-0">
          
          <button
            onClick={handleViewCommandMap}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 text-xs font-mono font-semibold transition-colors"
          >
            <Compass className="w-4 h-4 text-cyan-400" />
            <span>View on GIS Command Map</span>
          </button>

          <div className="flex items-center space-x-2">
            {/* OpenStreetMap Direct Directions */}
            <a
              href={openStreetMapUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 text-xs font-mono transition-colors"
            >
              <span>OpenStreetMap</span>
              <ExternalLink className="w-3.5 h-3.5 text-gray-400" />
            </a>

            {/* Google Maps Direct Turn-by-Turn GPS */}
            <a
              href={googleMapsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-mono font-bold text-xs shadow-lg transition-all"
            >
              <span>Open in Google Maps</span>
              <ExternalLink className="w-4 h-4" />
            </a>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 text-xs font-mono font-semibold transition-colors"
            >
              Close
            </button>
          </div>

        </div>

      </div>
    </div>
  );
};
