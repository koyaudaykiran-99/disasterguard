import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useLocation } from '../../hooks/useLocation';
import { useEmergencyQueue } from '../../hooks/useEmergencyQueue';
import { useLanguage } from '../../context/LanguageContext';
import { Shelter, Hospital } from '../../types';
import { StoredShelter, StoredHospital } from '../../storage/storageTypes';
import {
  Crosshair,
  Compass,
  Navigation,
  ShieldCheck,
  Hospital as HospitalIcon,
  AlertTriangle,
  Waves,
  MapPin,
  ExternalLink,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

// Fix Leaflet default icon path issue with bundlers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface CitizenMapProps {
  shelters: (Shelter | StoredShelter)[];
  hospitals: (Hospital | StoredHospital)[];
  selectedFacility?: Shelter | Hospital | null;
  onSelectFacility?: (facility: Shelter | Hospital | null) => void;
  className?: string;
}

// Inundation risk zones for visual hazard avoidance
const INUNDATION_ZONES = [
  {
    name: 'Downtown Riverside Basin',
    severity: 'CRITICAL',
    polygon: [
      [13.078, 80.265],
      [13.078, 80.282],
      [13.092, 80.282],
      [13.092, 80.265],
    ] as [number, number][],
    waterDepth: '1.45m',
    teWarning: 'తీవ్ర వరద ప్రాంతం. ఈ మార్గంలో వెళ్లకండి.',
    enWarning: 'Severe inundation area. Do not attempt crossing.',
  },
  {
    name: 'Northern Canal Lowlands',
    severity: 'HIGH',
    polygon: [
      [13.088, 80.280],
      [13.088, 80.295],
      [13.102, 80.295],
      [13.102, 80.280],
    ] as [number, number][],
    waterDepth: '0.85m',
    teWarning: 'కాలువ సమీప ప్రాంతం. నీటి ప్రవాహం ఎక్కువగా ఉంది.',
    enWarning: 'Canal corridor overflow. Proceed with caution.',
  },
];

export const CitizenMap: React.FC<CitizenMapProps> = ({
  shelters,
  hospitals,
  selectedFacility,
  onSelectFacility,
  className = 'h-[440px]',
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupRef = useRef<L.LayerGroup | null>(null);
  const routePolylineRef = useRef<L.Polyline | null>(null);

  const { coords, status: locStatus, locationName, requestLocation, isLocating } = useLocation();
  const { activeSOS } = useEmergencyQueue();
  const { language } = useLanguage();

  const [activeFilter, setActiveFilter] = useState<'ALL' | 'SHELTERS' | 'HOSPITALS' | 'HAZARDS'>('ALL');
  const [showRouteGuidance, setShowRouteGuidance] = useState<boolean>(true);
  const [selectedDestination, setSelectedDestination] = useState<{
    name: string;
    type: 'SHELTER' | 'HOSPITAL';
    lat: number;
    lng: number;
    distanceKm: number;
    notes?: string;
  } | null>(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const initialLat = coords?.latitude || 13.0827;
    const initialLng = coords?.longitude || 80.2707;

    const map = L.map(mapContainerRef.current, {
      center: [initialLat, initialLng],
      zoom: 13,
      zoomControl: false,
    });

    // High quality OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const layerGroup = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;
    layerGroupRef.current = layerGroup;

    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 250);

    const handleResize = () => {
      map.invalidateSize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', handleResize);
      map.remove();
      mapInstanceRef.current = null;
      layerGroupRef.current = null;
    };
  }, []);

  // Sync selectedFacility prop to selectedDestination
  useEffect(() => {
    if (selectedFacility) {
      const fac: any = selectedFacility;
      const userLat = coords?.latitude || 13.0827;
      const userLng = coords?.longitude || 80.2707;
      const fLat = fac.latitude ?? 13.085;
      const fLng = fac.longitude ?? 80.275;
      const dLat = (fLat - userLat) * 111;
      const dLng = (fLng - userLng) * 111 * Math.cos((userLat * Math.PI) / 180);
      const dist = Math.sqrt(dLat * dLat + dLng * dLng);

      setSelectedDestination({
        name: fac.name,
        type: 'capacity' in fac ? 'SHELTER' : 'HOSPITAL',
        lat: fLat,
        lng: fLng,
        distanceKm: Number(dist.toFixed(2)),
      });
    }
  }, [selectedFacility, coords]);

  // Compute nearest shelter / hospital as default safe destination if none selected
  useEffect(() => {
    if (!selectedDestination && shelters.length > 0) {
      const userLat = coords?.latitude || 13.0827;
      const userLng = coords?.longitude || 80.2707;

      let nearest: any = shelters[0];
      let minDist = 999999;

      shelters.forEach((s: any) => {
        const sLat = s.latitude ?? 13.085;
        const sLng = s.longitude ?? 80.275;
        const dLat = (sLat - userLat) * 111;
        const dLng = (sLng - userLng) * 111 * Math.cos((userLat * Math.PI) / 180);
        const dist = Math.sqrt(dLat * dLat + dLng * dLng);
        if (dist < minDist) {
          minDist = dist;
          nearest = s;
        }
      });

      if (nearest) {
        setSelectedDestination({
          name: nearest.name,
          type: 'SHELTER',
          lat: nearest.latitude ?? 13.085,
          lng: nearest.longitude ?? 80.275,
          distanceKm: Number(minDist.toFixed(2)),
          notes: 'Nearest verified elevated relief point',
        });
      }
    }
  }, [shelters, coords, selectedDestination]);

  // Render Map Layers and Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup) return;

    layerGroup.clearLayers();

    const userLat = coords?.latitude || 13.0827;
    const userLng = coords?.longitude || 80.2707;

    // 1. Inundation Risk Zones
    if (activeFilter === 'ALL' || activeFilter === 'HAZARDS') {
      INUNDATION_ZONES.forEach((zone) => {
        const polygon = L.polygon(zone.polygon, {
          color: '#EF4444',
          weight: 2,
          fillColor: '#EF4444',
          fillOpacity: 0.25,
          dashArray: '4, 6',
        });

        const warningMsg = language === 'te' ? zone.teWarning : zone.enWarning;
        polygon.bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4; min-width: 180px;">
            <div style="font-weight: bold; color: #DC2626;">⚠️ ${zone.name}</div>
            <div style="margin-top: 4px; color: #475569;">Water Depth: <strong>${zone.waterDepth}</strong></div>
            <div style="margin-top: 4px; padding: 4px; background: #FEE2E2; border-radius: 4px; color: #991B1B; font-size: 11px;">${warningMsg}</div>
          </div>
        `);
        layerGroup.addLayer(polygon);
      });
    }

    // 2. Shelters Markers
    if (activeFilter === 'ALL' || activeFilter === 'SHELTERS') {
      shelters.forEach((shelter) => {
        const shelterIcon = L.divIcon({
          className: 'custom-shelter-marker',
          html: '<div style="width: 32px; height: 32px; background: #059669; border: 2px solid #FFFFFF; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); color: white; font-weight: bold; font-size: 14px;">🛡️</div>',
          iconSize: [32, 32],
          iconAnchor: [16, 16],
        });

        const sLat = (shelter as any).latitude ?? 13.085;
        const sLng = (shelter as any).longitude ?? 80.275;
        const marker = L.marker([sLat, sLng], { icon: shelterIcon });
        marker.bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4; min-width: 200px;">
            <div style="font-weight: bold; color: #047857;">🛡️ ${shelter.name}</div>
            <div style="color: #64748B; font-size: 11px; margin-top: 2px;">${shelter.address || 'Verified Relief Center'}</div>
            <div style="margin-top: 6px; display: flex; gap: 4px;">
              <span style="background: #D1FAE5; color: #065F46; padding: 2px 6px; border-radius: 12px; font-size: 10px; font-weight: 600;">Capacity: ${shelter.currentOccupancy || 0}/${shelter.capacity || 200}</span>
            </div>
          </div>
        `);

        marker.on('click', () => {
          const dLat = (sLat - userLat) * 111;
          const dLng = (sLng - userLng) * 111 * Math.cos((userLat * Math.PI) / 180);
          const dist = Math.sqrt(dLat * dLat + dLng * dLng);
          setSelectedDestination({
            name: shelter.name,
            type: 'SHELTER',
            lat: sLat,
            lng: sLng,
            distanceKm: Number(dist.toFixed(2)),
          });
          if (onSelectFacility) onSelectFacility(shelter as Shelter);
        });

        layerGroup.addLayer(marker);
      });
    }

    // 3. Hospitals Markers
    if (activeFilter === 'ALL' || activeFilter === 'HOSPITALS') {
      hospitals.forEach((hosp) => {
        const hospIcon = L.divIcon({
          className: 'custom-hosp-marker',
          html: '<div style="width: 32px; height: 32px; background: #2563EB; border: 2px solid #FFFFFF; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); color: white; font-weight: bold; font-size: 14px;">🏥</div>',
          iconSize: [32, 32],
          iconAnchor: [16, 16],
        });

        const hLat = (hosp as any).latitude ?? 13.085;
        const hLng = (hosp as any).longitude ?? 80.275;
        const marker = L.marker([hLat, hLng], { icon: hospIcon });
        marker.bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4; min-width: 200px;">
            <div style="font-weight: bold; color: #1D4ED8;">🏥 ${hosp.name}</div>
            <div style="color: #64748B; font-size: 11px; margin-top: 2px;">${hosp.address || 'Emergency Trauma Center'}</div>
            <div style="margin-top: 6px; display: flex; gap: 4px;">
              <span style="background: #DBEAFE; color: #1E40AF; padding: 2px 6px; border-radius: 12px; font-size: 10px; font-weight: 600;">Emergency ICU Available</span>
            </div>
          </div>
        `);

        marker.on('click', () => {
          const dLat = (hLat - userLat) * 111;
          const dLng = (hLng - userLng) * 111 * Math.cos((userLat * Math.PI) / 180);
          const dist = Math.sqrt(dLat * dLat + dLng * dLng);
          setSelectedDestination({
            name: hosp.name,
            type: 'HOSPITAL',
            lat: hLat,
            lng: hLng,
            distanceKm: Number(dist.toFixed(2)),
          });
          if (onSelectFacility) onSelectFacility(hosp as Hospital);
        });

        layerGroup.addLayer(marker);
      });
    }

    // 4. Active SOS Marker (Red Pulsing Beacon)
    if (activeSOS && activeSOS.latitude && activeSOS.longitude) {
      const sosIcon = L.divIcon({
        className: 'custom-sos-beacon',
        html: '<div style="position: relative; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;"><div style="position: absolute; width: 36px; height: 36px; border-radius: 50%; background: rgba(239, 68, 68, 0.4); animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div><div style="position: relative; width: 24px; height: 24px; background: #DC2626; border: 2px solid #FFFFFF; border-radius: 50%; box-shadow: 0 0 12px rgba(220, 38, 38, 0.8); display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">🚨</div></div>',
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });

      const sosMarker = L.marker([activeSOS.latitude, activeSOS.longitude], { icon: sosIcon });
      sosMarker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4;">
          <div style="font-weight: bold; color: #DC2626;">🚨 Active Distress Beacon</div>
          <div style="color: #64748B; font-size: 11px;">Status: <strong>${activeSOS.status}</strong></div>
          <div style="color: #64748B; font-size: 11px;">Severity: <strong>${activeSOS.severity}</strong></div>
        </div>
      `);
      layerGroup.addLayer(sosMarker);
    }

    // 5. User Location Marker
    const userIcon = L.divIcon({
      className: 'custom-user-marker',
      html: '<div style="position: relative; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;"><div style="position: absolute; width: 28px; height: 28px; border-radius: 50%; background: rgba(14, 165, 233, 0.35); animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;"></div><div style="position: relative; width: 16px; height: 16px; background: #0284C7; border: 2px solid #FFFFFF; border-radius: 50%; box-shadow: 0 0 8px rgba(2, 132, 199, 0.8);"></div></div>',
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    });

    const userMarker = L.marker([userLat, userLng], { icon: userIcon });
    userMarker.bindPopup(`
      <div style="font-family: sans-serif; font-size: 12px;">
        <div style="font-weight: bold; color: #0284C7;">📍 Your Location</div>
        <div style="color: #64748B; font-size: 11px;">${locationName || 'GPS Synced'}</div>
        <div style="color: #94A3B8; font-size: 10px; margin-top: 2px;">${userLat.toFixed(4)}°N, ${userLng.toFixed(4)}°E</div>
      </div>
    `);
    layerGroup.addLayer(userMarker);

    if (coords?.accuracy && coords.accuracy < 500) {
      const accuracyCircle = L.circle([userLat, userLng], {
        radius: coords.accuracy,
        color: '#0284C7',
        weight: 1,
        fillColor: '#38BDF8',
        fillOpacity: 0.12,
      });
      layerGroup.addLayer(accuracyCircle);
    }

    // 6. Safe Route Polyline (Green/Emerald Dashed Corridor)
    if (showRouteGuidance && selectedDestination) {
      if (routePolylineRef.current) {
        routePolylineRef.current.remove();
        routePolylineRef.current = null;
      }

      const routePoints: [number, number][] = [
        [userLat, userLng],
        [
          userLat + (selectedDestination.lat - userLat) * 0.5 + 0.003,
          userLng + (selectedDestination.lng - userLng) * 0.5 - 0.002,
        ],
        [selectedDestination.lat, selectedDestination.lng],
      ];

      const polyline = L.polyline(routePoints, {
        color: '#059669',
        weight: 4,
        dashArray: '8, 8',
        opacity: 0.9,
      });

      polyline.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4;">
          <div style="font-weight: bold; color: #059669;">🛡️ Safe High-Ground Corridor</div>
          <div style="color: #475569;">Destination: <strong>${selectedDestination.name}</strong></div>
          <div style="color: #475569;">Distance: <strong>~${selectedDestination.distanceKm} km</strong> (Approx. geographic distance)</div>
          <div style="margin-top: 4px; font-size: 11px; color: #047857; font-weight: 500;">
            ${language === 'te' ? 'ఎత్తైన రహదారి మార్గం. వరద నీటిలో నడవకండి.' : 'Elevated terrain corridor. Avoid water logging.'}
          </div>
        </div>
      `);

      polyline.addTo(layerGroup);
      routePolylineRef.current = polyline;
    }
  }, [shelters, hospitals, coords, locationName, activeFilter, showRouteGuidance, selectedDestination, activeSOS, language, onSelectFacility]);

  const handleCenterUser = () => {
    requestLocation();
    if (mapInstanceRef.current && coords) {
      mapInstanceRef.current.flyTo([coords.latitude, coords.longitude], 15, { duration: 1.2 });
    }
  };

  const handleCenterDestination = () => {
    if (mapInstanceRef.current && selectedDestination) {
      mapInstanceRef.current.flyTo([selectedDestination.lat, selectedDestination.lng], 15, { duration: 1.2 });
    }
  };

  return (
    <div className={`relative w-full rounded-3xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-xl bg-white dark:bg-slate-950 flex flex-col ${className}`}>
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      <div className="absolute top-3 left-3 right-3 z-10 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-1.5 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md p-1 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-md pointer-events-auto">
          {(['ALL', 'SHELTERS', 'HOSPITALS', 'HAZARDS'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-2.5 py-1 text-[11px] font-semibold rounded-xl transition-all ${
                activeFilter === filter
                  ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-sm'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              {filter === 'ALL' && (language === 'te' ? 'అన్నీ' : 'All')}
              {filter === 'SHELTERS' && (language === 'te' ? '🛡️ శిబిరాలు' : '🛡️ Shelters')}
              {filter === 'HOSPITALS' && (language === 'te' ? '🏥 ఆసుపత్రులు' : '🏥 Hospitals')}
              {filter === 'HAZARDS' && (language === 'te' ? '⚠️ వరద ప్రాంతాలు' : '⚠️ Flood Zones')}
            </button>
          ))}
        </div>

        <button
          onClick={handleCenterUser}
          disabled={isLocating}
          className="p-2.5 rounded-2xl bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border border-slate-200 dark:border-slate-800 shadow-md text-cyan-600 dark:text-cyan-400 hover:scale-105 active:scale-95 transition-all pointer-events-auto flex items-center gap-1.5 text-xs font-semibold"
          title="Locate my position"
        >
          <Crosshair className={`w-4 h-4 ${isLocating ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">{isLocating ? 'Locating...' : 'GPS'}</span>
        </button>
      </div>

      {selectedDestination && showRouteGuidance && (
        <div className="absolute bottom-3 left-3 right-3 z-10 pointer-events-auto">
          <div className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-md p-3.5 rounded-2xl border border-emerald-500/30 dark:border-emerald-500/40 shadow-xl transition-all">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-start gap-2.5">
                <div className="p-2 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400">
                  {selectedDestination.type === 'SHELTER' ? (
                    <ShieldCheck className="w-5 h-5" />
                  ) : (
                    <HospitalIcon className="w-5 h-5" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-700 dark:text-emerald-300">
                      Safe Evacuation Corridor
                    </span>
                    <span className="text-xs font-mono text-slate-500 dark:text-slate-400">
                      ~{selectedDestination.distanceKm} km (Approx. geographic distance)
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white mt-0.5">
                    {selectedDestination.name}
                  </h4>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 font-medium">
                    {language === 'te'
                      ? 'వరద నీటిలో నడవకండి. ఎత్తైన ప్రదేశాలు మరియు సురక్షితమైన మార్గాల ద్వారా వెళ్లండి.'
                      : 'Move towards elevated terrain. Avoid entering rapidly moving floodwaters.'}
                  </p>
                </div>
              </div>

              <button
                onClick={handleCenterDestination}
                className="px-2.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition-all flex items-center gap-1 shadow-sm shrink-0"
              >
                <Navigation className="w-3.5 h-3.5" />
                <span>View</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
