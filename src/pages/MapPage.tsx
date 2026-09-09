import React, { useState } from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { DisasterMap } from '../components/map/DisasterMap';
import { useDisaster } from '../context/DisasterContext';
import { MapPin, Layers, Database, Compass, CheckCircle2 } from 'lucide-react';

export const MapPage: React.FC = () => {
  const { markers, postGisLogs, filterSafeZonesByRadius } = useDisaster();
  const [selectedRadius, setSelectedRadius] = useState<number>(5.0);

  const handleRadiusChange = (radius: number) => {
    setSelectedRadius(radius);
    filterSafeZonesByRadius(radius);
  };

  return (
    <PageTransition className="p-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-gray-800">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            <Compass className="w-6 h-6 text-cyan-400" />
            GIS Command Map & PostGIS Spatial Engine
          </h2>
          <p className="text-xs text-gray-400 font-mono mt-1">
            Spatial Geometry Vector Overlay & Real-Time Animated Markers
          </p>
        </div>

        {/* PostGIS Spatial Radius Query Control */}
        <div className="flex items-center space-x-3 bg-gray-900 px-4 py-2 rounded-xl border border-gray-800 text-xs font-mono">
          <Database className="w-4 h-4 text-emerald-400" />
          <span className="text-gray-300">ST_DWithin Radius:</span>
          {[3, 5, 10, 20].map((r) => (
            <button
              key={r}
              onClick={() => handleRadiusChange(r)}
              className={`px-2.5 py-1 rounded-lg transition-colors ${
                selectedRadius === r
                  ? 'bg-blue-600 text-white font-bold'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {r}km
            </button>
          ))}
        </div>
      </div>

      {/* Main Map & PostGIS Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Main Map */}
        <div className="lg:col-span-8">
          <DisasterMap height="h-[600px]" />
        </div>

        {/* Side Panel: Active GIS Layer Markers & PostGIS Query Inspector */}
        <div className="lg:col-span-4 space-y-4">
          <div className="glass-panel p-5 rounded-2xl border border-gray-800 space-y-4">
            <h3 className="text-sm font-bold font-mono text-gray-200 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Active GIS Markers ({markers.length})
            </h3>

            <div className="space-y-2.5 max-h-[260px] overflow-y-auto pr-1">
              {markers.map((m) => (
                <div
                  key={m.id}
                  className="p-3 rounded-xl bg-gray-900/80 border border-gray-800 flex items-start space-x-3 text-xs"
                >
                  <MapPin
                    className={`w-4 h-4 mt-0.5 ${
                      m.type === 'EMERGENCY'
                        ? 'text-rose-400'
                        : m.type === 'DISASTER'
                        ? 'text-orange-400'
                        : 'text-emerald-400'
                    }`}
                  />
                  <div>
                    <div className="font-bold text-gray-200">{m.title}</div>
                    <div className="text-[10px] font-mono text-gray-400 mt-0.5">{m.details}</div>
                    <div className="text-[10px] font-mono text-cyan-400 mt-1">
                      [{m.coordinates[0]}, {m.coordinates[1]}]
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* PostGIS Execution Log */}
          <div className="glass-panel p-5 rounded-2xl border border-gray-800 space-y-3 font-mono">
            <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              PostgreSQL / PostGIS Log
            </h3>
            <div className="space-y-2 text-[11px]">
              {postGisLogs.map((log, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800/80">
                  <div className="text-cyan-300 font-bold">
                    SELECT * FROM {log.table} WHERE {log.queryType}(geom, ST_MakePoint(
                    {log.centerCoordinates[1]}, {log.centerCoordinates[0]}), {log.radiusKm}000);
                  </div>
                  <div className="flex items-center justify-between text-gray-400 text-[10px] mt-1.5">
                    <span>Rows: {log.returnedRowsCount}</span>
                    <span className="text-emerald-400 font-semibold">{log.executionTimeMs} ms</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};
