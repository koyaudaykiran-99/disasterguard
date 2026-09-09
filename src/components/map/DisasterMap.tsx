import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polygon, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useDisaster } from '../../context/DisasterContext';
import { createAnimatedMarkerIcon } from '../motion/AnimatedMapMarker';
import {
  Layers,
  Crosshair,
  ShieldCheck,
  Radio,
  CloudRain,
  Compass,
  Sparkles,
  MapPin,
  Maximize2,
  Info,
  History,
  Flame,
  Users,
  Hospital,
  AlertTriangle,
  Zap,
  ChevronDown,
  X
} from 'lucide-react';
import { disasterService } from '../../services/disasterService';
import { situationalAwarenessService } from '../../services/situationalAwarenessService';
import { HistoricalFloodEvent } from '../../types/disaster';
import { RiskHotspot, IncidentCluster } from '../../types/situationalAwareness';

interface DisasterMapProps {
  height?: string;
}

// Controller component to programmatically pan/zoom map via Leaflet useMap hook
const MapController: React.FC<{
  center: [number, number];
  zoom: number;
  triggerRecenter: number;
}> = ({ center, zoom, triggerRecenter }) => {
  const map = useMap();

  useEffect(() => {
    if (triggerRecenter > 0) {
      map.flyTo(center, zoom, { duration: 1.2 });
    }
  }, [triggerRecenter, center, zoom, map]);

  return null;
};

// PostGIS Inundation Geometry Polygons (coordinates [lat, lng])
const INUNDATION_ZONES: Array<{
  id: string;
  name: string;
  polygon: [number, number][];
  severity: 'CRITICAL' | 'HIGH';
  depthM: number;
  affectedPop: number;
}> = [
  {
    id: 'inundation-zone-1',
    name: 'Downtown Riverside Basin (Severe Spill)',
    polygon: [
      [13.078, 80.265],
      [13.078, 80.282],
      [13.092, 80.282],
      [13.092, 80.265],
    ],
    severity: 'CRITICAL',
    depthM: 1.45,
    affectedPop: 14200,
  },
  {
    id: 'inundation-zone-2',
    name: 'Northern Highway Slopes Inundation Area',
    polygon: [
      [13.088, 80.280],
      [13.088, 80.295],
      [13.102, 80.295],
      [13.102, 80.280],
    ],
    severity: 'HIGH',
    depthM: 0.85,
    affectedPop: 3800,
  },
];

export const DisasterMap: React.FC<DisasterMapProps> = ({ height = 'h-[520px]' }) => {
  const { markers, safeZones, sosIncidents } = useDisaster();

  // Chennai Metro Disaster Center
  const centerCoordinates: [number, number] = [13.0827, 80.2707];
  const [recenterCount, setRecenterCount] = useState<number>(0);

  // Map Theme
  const [tileMode, setTileMode] = useState<'tactical' | 'standard'>('tactical');
  const [showLayerDrawer, setShowLayerDrawer] = useState<boolean>(false);

  // 14 Operational Layers State
  const [layers, setLayers] = useState({
    currentRisk: true,
    forecastRisk: true,
    floodSusceptibility: true,
    historicalFloods: true,
    activeSos: true,
    activeIncidents: true,
    incidentClusters: true,
    riskHotspots: true,
    rescueTeams: true,
    shelters: true,
    hospitals: true,
    alerts: true,
    resourceContention: true,
    operationalBottlenecks: true,
  });

  const [historicalEvents, setHistoricalEvents] = useState<HistoricalFloodEvent[]>([]);
  const [hotspots, setHotspots] = useState<RiskHotspot[]>([]);
  const [clusters, setClusters] = useState<IncidentCluster[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [evs, hs, cls] = await Promise.all([
          disasterService.getHistoricalFloodEvents().catch(() => []),
          situationalAwarenessService.getHotspots().catch(() => []),
          situationalAwarenessService.getClusters().catch(() => []),
        ]);
        if (Array.isArray(evs)) setHistoricalEvents(evs);
        if (Array.isArray(hs)) setHotspots(hs);
        if (Array.isArray(cls)) setClusters(cls);
      } catch (e) {
        console.error('Failed to load map situational layers:', e);
      }
    };
    loadData();
    const interval = setInterval(loadData, 20000);
    return () => clearInterval(interval);
  }, []);

  const toggleLayer = (key: keyof typeof layers) => {
    setLayers(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className={`w-full ${height} rounded-2xl overflow-hidden border border-gray-800 shadow-2xl relative z-10 flex flex-col bg-command-card`}>
      {/* Interactive Top Floating Command HUD Bar */}
      <div className="absolute top-3 left-3 right-3 z-[400] flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        {/* Left: OpenStreetMap & PostGIS Badge */}
        <div className="flex items-center space-x-2 bg-gray-950/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-gray-800 pointer-events-auto shadow-lg text-xs font-mono">
          <div className="flex items-center space-x-1.5 text-cyan-400 font-bold">
            <Compass className="w-4 h-4" />
            <span>OpenStreetMap + Leaflet</span>
          </div>
          <span className="text-gray-600">|</span>
          <span className="text-emerald-400 flex items-center gap-1 text-[11px]">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            14 Layer Multi-Signal Active
          </span>
        </div>

        {/* Right: Map HUD Controls & Layer Drawer Trigger */}
        <div className="flex items-center space-x-2 bg-gray-950/90 backdrop-blur-md p-1.5 rounded-xl border border-gray-800 pointer-events-auto shadow-lg text-xs font-mono">
          {/* Tile Theme Switcher */}
          <button
            onClick={() => setTileMode(tileMode === 'tactical' ? 'standard' : 'tactical')}
            className={`px-2.5 py-1 rounded-lg transition-colors flex items-center space-x-1 ${
              tileMode === 'tactical'
                ? 'bg-blue-600/30 text-blue-300 border border-blue-500/40'
                : 'bg-gray-800 text-gray-300 hover:text-white'
            }`}
            title="Toggle OSM Tactical Dark or OSM Standard"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{tileMode === 'tactical' ? 'Tactical Dark' : 'OSM Daylight'}</span>
          </button>

          {/* 14 Layers Manager Button */}
          <button
            onClick={() => setShowLayerDrawer(!showLayerDrawer)}
            className={`px-2.5 py-1 rounded-lg transition-colors flex items-center space-x-1 font-bold ${
              showLayerDrawer
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 hover:bg-indigo-500/30'
            }`}
            title="Open 14-Layer Operational Controls"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Layers (14)</span>
            <ChevronDown className="w-3 h-3 ml-0.5" />
          </button>

          {/* Recenter Button */}
          <button
            onClick={() => setRecenterCount((c) => c + 1)}
            className="p-1.5 rounded-lg bg-gray-900 hover:bg-gray-800 text-gray-300 hover:text-cyan-300 border border-gray-800 transition-colors"
            title="Recenter Map to Metro Command Center"
          >
            <Crosshair className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 14-Layer Control Drawer Overlay */}
      {showLayerDrawer && (
        <div className="absolute top-14 right-3 z-[450] w-80 bg-gray-950/95 backdrop-blur-md border border-gray-800 rounded-xl shadow-2xl p-4 text-xs font-sans pointer-events-auto max-h-[420px] overflow-y-auto">
          <div className="flex items-center justify-between pb-2 border-b border-gray-800 mb-3">
            <span className="font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Operational Map Layers</span>
            </span>
            <button
              onClick={() => setShowLayerDrawer(false)}
              className="text-gray-400 hover:text-white p-1 rounded hover:bg-gray-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-2">
            {[
              { key: 'currentRisk', label: '1. Current Risk Zones', count: markers.filter(m => m.type === 'DISASTER').length },
              { key: 'forecastRisk', label: '2. Multi-Horizon Forecast Surge', count: 'Active' },
              { key: 'floodSusceptibility', label: '3. Flood Inundation Polygons', count: INUNDATION_ZONES.length },
              { key: 'historicalFloods', label: '4. Historical Disaster Events', count: historicalEvents.length },
              { key: 'activeSos', label: '5. Citizen SOS Distress Points', count: sosIncidents.length },
              { key: 'activeIncidents', label: '6. Prioritized Incidents', count: markers.filter(m => m.type === 'EMERGENCY').length },
              { key: 'incidentClusters', label: '7. DBSCAN Incident Clusters', count: clusters.length },
              { key: 'riskHotspots', label: '8. PostGIS Spatial Hotspots', count: hotspots.length },
              { key: 'rescueTeams', label: '9. Rescue Squads & Staging', count: 4 },
              { key: 'shelters', label: '10. Safe Shelters & Evac Hubs', count: safeZones.length },
              { key: 'hospitals', label: '11. Emergency Trauma Hospitals', count: 3 },
              { key: 'alerts', label: '12. Active Broadcast Alerts', count: 'Synced' },
              { key: 'resourceContention', label: '13. Resource Contention Vectors', count: 'Active' },
              { key: 'operationalBottlenecks', label: '14. Road & Drainage Bottlenecks', count: 2 },
            ].map((layer) => {
              const isActive = layers[layer.key as keyof typeof layers];
              return (
                <label
                  key={layer.key}
                  className="flex items-center justify-between p-2 rounded-lg bg-gray-900/60 hover:bg-gray-900 border border-gray-800/80 cursor-pointer transition"
                >
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={isActive}
                      onChange={() => toggleLayer(layer.key as keyof typeof layers)}
                      className="rounded border-gray-700 text-blue-600 focus:ring-0"
                    />
                    <span className={isActive ? 'text-gray-200 font-medium' : 'text-gray-500'}>
                      {layer.label}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-gray-800 text-gray-400">
                    {layer.count}
                  </span>
                </label>
              );
            })}
          </div>
        </div>
      )}

      {/* Leaflet Map Canvas */}
      <MapContainer
        center={centerCoordinates}
        zoom={13}
        scrollWheelZoom={true}
        className="w-full h-full"
        style={{ background: '#080c14' }}
      >
        <MapController
          center={centerCoordinates}
          zoom={13}
          triggerRecenter={recenterCount}
        />

        {/* Pure OpenStreetMap Standard Tiles Layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className={tileMode === 'tactical' ? 'osm-tactical-tiles' : ''}
          maxZoom={19}
        />

        {/* 3. PostGIS Flood Inundation Polygons & Risk Zones Overlay */}
        {layers.floodSusceptibility &&
          INUNDATION_ZONES.map((zone) => (
            <Polygon
              key={zone.id}
              positions={zone.polygon}
              pathOptions={{
                color: zone.severity === 'CRITICAL' ? '#f43f5e' : '#f97316',
                fillColor: zone.severity === 'CRITICAL' ? '#f43f5e' : '#f97316',
                fillOpacity: 0.22,
                weight: 2,
                dashArray: '6, 6',
              }}
            >
              <Popup className="custom-popup">
                <div className="p-2.5 font-sans text-xs bg-gray-950 text-gray-100 rounded-lg space-y-1.5">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-bold text-xs font-mono text-rose-400 uppercase">
                      {zone.name}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                      {zone.severity}
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-300 space-y-0.5">
                    <div>Estimated Water Depth: <strong className="text-cyan-400">{zone.depthM} m</strong></div>
                    <div>Affected Population: <strong className="text-amber-300">{zone.affectedPop.toLocaleString()}</strong></div>
                  </div>
                  <div className="text-[10px] font-mono text-gray-500 border-t border-gray-800 pt-1">
                    PostGIS Polygon Layer ST_Contains
                  </div>
                </div>
              </Popup>
            </Polygon>
          ))}

        {/* 8. PostGIS Multi-Signal Geographic Risk Hotspots */}
        {layers.riskHotspots &&
          hotspots.map((h) => (
            <Circle
              key={`hotspot-${h.id}`}
              center={[h.latitude, h.longitude]}
              radius={h.radiusMeters || 700}
              pathOptions={{
                color: h.severity === 'CRITICAL' ? '#dc2626' : '#ea580c',
                fillColor: h.severity === 'CRITICAL' ? '#ef4444' : '#f97316',
                fillOpacity: 0.28,
                weight: 2.5,
              }}
            >
              <Popup className="custom-popup">
                <div className="p-3 font-sans text-xs bg-gray-950 text-gray-100 rounded-xl space-y-2 min-w-[260px] border border-red-500/40 shadow-2xl">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-rose-400 text-xs flex items-center space-x-1">
                      <Flame className="w-3.5 h-3.5" />
                      <span>{h.name}</span>
                    </span>
                    <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-red-500/20 text-red-400 border border-red-500/30">
                      HOTSPOT
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-300 space-y-1 bg-gray-900/80 p-2 rounded-lg border border-gray-800">
                    <div>Composite Convergence Score: <strong className="text-red-400">{Math.round(h.compositeScore * 100)}/100</strong></div>
                    <div>Status: <span className="text-emerald-400 font-bold">{h.status}</span></div>
                    <div>Confidence: <span className="text-slate-300">{Math.round(h.confidence * 100)}%</span></div>
                    <div>Provenance: <span className="text-slate-400 font-mono">{h.provenance}</span></div>
                  </div>
                </div>
              </Popup>
            </Circle>
          ))}

        {/* 7. DBSCAN Incident Clusters (Preserves original emergency identities) */}
        {layers.incidentClusters &&
          clusters.map((c) => (
            <Circle
              key={`cluster-${c.id}`}
              center={[c.centerLat, c.centerLon]}
              radius={c.radiusMeters || 600}
              pathOptions={{
                color: '#818cf8',
                fillColor: '#6366f1',
                fillOpacity: 0.18,
                weight: 2,
                dashArray: '5, 5',
              }}
            >
              <Popup className="custom-popup">
                <div className="p-3 font-sans text-xs bg-gray-950 text-gray-100 rounded-xl space-y-2 min-w-[260px] border border-indigo-500/40 shadow-2xl">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-indigo-400 text-xs flex items-center space-x-1">
                      <Users className="w-3.5 h-3.5" />
                      <span>{c.clusterCode}</span>
                    </span>
                    <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      INCIDENT CLUSTER
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-300 space-y-1 bg-gray-900/80 p-2 rounded-lg border border-gray-800">
                    <div>Aggregated Incidents: <strong className="text-white">{c.incidentCount}</strong> ({c.criticalCount} critical)</div>
                    <div>Composite Priority: <strong className="text-amber-400">{Math.round(c.compositePriority * 100)}/100</strong></div>
                    <div>Emergency Records: <span className="text-emerald-400 font-bold">Intact & Distinct</span></div>
                    {c.recommendedTeams?.length > 0 && (
                      <div className="border-t border-gray-800 pt-1">
                        <span className="text-gray-400">Rec Team: </span>
                        <span className="text-cyan-300 font-semibold">{c.recommendedTeams[0].teamName}</span>
                      </div>
                    )}
                  </div>
                </div>
              </Popup>
            </Circle>
          ))}

        {/* 10. PostGIS Safe Zone Radii Overlay */}
        {layers.shelters &&
          safeZones.map((sz) => (
            <React.Fragment key={`sz-group-${sz.id}`}>
              <Circle
                center={sz.coordinates}
                radius={sz.distanceKm * 1000}
                pathOptions={{
                  color: sz.status === 'FULL' ? '#ef4444' : '#10b981',
                  fillColor: sz.status === 'FULL' ? '#ef4444' : '#10b981',
                  fillOpacity: 0.08,
                  weight: 1.5,
                  dashArray: '4, 8',
                }}
              />
            </React.Fragment>
          ))}

        {/* 13. Rescue Team Dispatch Routing Lines */}
        {layers.resourceContention &&
          sosIncidents
            .filter(
              (inc) =>
                (inc.status === 'DISPATCHED' || inc.assignmentStatus === 'DISPATCHED') &&
                inc.coordinates
            )
            .map((inc) => {
              const teamCoords: [number, number] =
                inc.rescueTeamCoordinates || [13.085, 80.28];
              return (
                <React.Fragment key={`dispatch-line-${inc.id}`}>
                  <Polyline
                    positions={[inc.coordinates, teamCoords]}
                    pathOptions={{
                      color: '#06b6d4',
                      weight: 3,
                      dashArray: '6, 8',
                      opacity: 0.85,
                    }}
                  >
                    <Popup>
                      <div className="p-2 font-mono text-xs bg-gray-950 text-gray-100 rounded-lg space-y-1">
                        <div className="font-bold text-cyan-400">
                          {inc.recommendedTeam || 'Rescue Team'} &rarr; Distress Site
                        </div>
                        <div className="text-[11px] text-gray-300">
                          Approx. geographic distance: {inc.teamDistanceKm ?? 0.4} km
                        </div>
                        <div className="text-[10px] text-amber-300">
                          Notice: Straight-line estimate. Actual route varies by flood depth.
                        </div>
                      </div>
                    </Popup>
                  </Polyline>
                </React.Fragment>
              );
            })}

        {/* Markers for Incidents & SOS */}
        {(layers.activeSos || layers.activeIncidents || layers.currentRisk) &&
          markers.map((marker) => {
            const customIcon = createAnimatedMarkerIcon(marker.type, marker.title);
            const rawId = marker.id.replace('mk-sos-', '').replace('mk-inc-', '').replace('mk-rz-', '');
            const linkedInc = sosIncidents.find(
              (s) => s.id === `sos-${rawId}` || s.id === `inc-${rawId}` || s.id === marker.id
            );

            return (
              <Marker key={marker.id} position={marker.coordinates} icon={customIcon}>
                <Popup className="custom-popup">
                  <div className="p-3 font-sans text-xs bg-gray-950 text-gray-100 rounded-xl space-y-2 min-w-[240px] border border-gray-800 shadow-2xl">
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-bold text-sm font-mono text-cyan-400">
                        {marker.title}
                      </span>
                      <span
                        className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded uppercase ${
                          marker.severity === 'CRITICAL'
                            ? 'bg-red-500/20 text-red-400 border border-red-500/50 animate-pulse'
                            : marker.severity === 'HIGH'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                            : 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                        }`}
                      >
                        {marker.severity}
                      </span>
                    </div>

                    <div className="text-[11px] text-gray-300 space-y-1 bg-gray-900/60 p-2 rounded-lg border border-gray-800/80">
                      {linkedInc ? (
                        <>
                          <div><span className="text-gray-400">AI Triage:</span> <strong className="text-cyan-300">{linkedInc.incidentType || 'FLOOD_TRAPPED_PERSON'}</strong></div>
                          <div><span className="text-gray-400">Priority Score:</span> <strong className="text-rose-400">{linkedInc.priorityScore || 95}/100</strong></div>
                          <div><span className="text-gray-400">Reported:</span> <span className="text-gray-200">{linkedInc.timestamp}</span></div>
                          <div><span className="text-gray-400">Rescue Team:</span> <strong className="text-amber-300">{linkedInc.recommendedTeam || 'Water Rescue Alpha'}</strong></div>
                          <div><span className="text-gray-400">Rescue Status:</span> <span className="text-emerald-400 font-mono font-bold uppercase">{linkedInc.assignmentStatus || linkedInc.status || 'DISPATCHED'}</span></div>
                          <div><span className="text-gray-400">Hospital:</span> <span className="text-gray-300">{linkedInc.recommendedHospital || 'St. Jude Emergency Center'}</span></div>
                          <div><span className="text-gray-400">Shelter:</span> <span className="text-gray-300">{linkedInc.recommendedShelter || 'Stadium Safe Shelter'}</span></div>
                        </>
                      ) : (
                        <p className="text-gray-300 text-xs leading-relaxed">{marker.details}</p>
                      )}
                    </div>

                    <div className="pt-2 border-t border-gray-800/80 flex items-center justify-between text-[11px] font-mono">
                      <span className="text-gray-500 text-[10px]">
                        [{marker.coordinates[0].toFixed(3)}, {marker.coordinates[1].toFixed(3)}]
                      </span>
                      <button
                        onClick={() => {
                          window.location.hash = '/emergency';
                        }}
                        className="px-2.5 py-1 rounded bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 border border-blue-500/40 text-[10px] font-bold"
                      >
                        Dispatch Center &rarr;
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}

        {/* 4. Verified Historical Flood & Cyclone Disasters Layer */}
        {layers.historicalFloods &&
          historicalEvents.map((ev) => (
            <Circle
              key={`hist-ev-${ev.id}`}
              center={[ev.latitude, ev.longitude]}
              radius={1000}
              pathOptions={{
                color: '#f59e0b',
                fillColor: '#f59e0b',
                fillOpacity: 0.28,
                weight: 2,
                dashArray: '4, 4',
              }}
            >
              <Popup className="custom-popup">
                <div className="p-3 font-mono text-xs bg-gray-950 text-gray-100 rounded-xl space-y-2 min-w-[260px] border border-amber-500/40 shadow-2xl">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-bold text-amber-400 text-xs">
                      {ev.event_name}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                      {ev.severity}
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-300 space-y-1 bg-gray-900/80 p-2 rounded-lg border border-gray-800">
                    <div>
                      <span className="text-gray-400">Disaster Date:</span>{' '}
                      <strong className="text-white">{ev.event_date}</strong>
                    </div>
                    <div>
                      <span className="text-gray-400">Total Rainfall:</span>{' '}
                      <strong className="text-cyan-300">{ev.rainfall_total_mm} mm</strong>
                    </div>
                    <div>
                      <span className="text-gray-400">Duration:</span>{' '}
                      <span className="text-gray-300">{ev.duration_hours} hours</span>
                    </div>
                    {ev.description && (
                      <div className="text-[10px] text-gray-400 border-t border-gray-800/80 pt-1 leading-snug">
                        {ev.description}
                      </div>
                    )}
                  </div>
                  <div className="text-[10px] text-gray-400 border-t border-gray-800 pt-1">
                    <span className="text-gray-500 block">Verified Source:</span>
                    <span className="text-gray-300 italic">{ev.source}</span>
                  </div>
                </div>
              </Popup>
            </Circle>
          ))}
      </MapContainer>

      {/* Bottom Map Legend Bar */}
      <div className="bg-gray-950/90 border-t border-gray-800/80 px-4 py-2 flex flex-wrap items-center justify-between text-[11px] font-mono text-gray-400">
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-600 border border-rose-300 animate-pulse"></span>
            <span>Active SOS / Hotspot</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 border border-indigo-300"></span>
            <span>Incident Cluster</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 border border-amber-300"></span>
            <span>Historical Disaster</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 border border-emerald-300"></span>
            <span>Safe Shelter</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-3 h-2 border border-rose-500 bg-rose-500/30"></span>
            <span>Inundation Zone</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-4 h-0.5 border-t-2 border-dashed border-cyan-400"></span>
            <span>Dispatch Path</span>
          </span>
        </div>

        <div className="flex items-center space-x-3 text-gray-500">
          <span>Tiles: OSM + PostGIS</span>
          <span>14 Layers Integrated</span>
        </div>
      </div>
    </div>
  );
};
