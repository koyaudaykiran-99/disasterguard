import React from 'react';
import { PageTransition } from '../components/motion/PageTransition';
import { AnimatedCard } from '../components/motion/AnimatedCard';
import { AnimatedCounter } from '../components/motion/AnimatedCounter';
import { RiskScore } from '../components/motion/RiskScore';
import { AIPredictionPanel } from '../components/motion/AIPredictionPanel';
import { EmergencySOSButton } from '../components/motion/EmergencySOSButton';
import { AlertCard } from '../components/motion/AlertCard';
import { StaggeredList } from '../components/motion/StaggeredList';
import { DisasterMap } from '../components/map/DisasterMap';
import { useDisaster } from '../context/DisasterContext';
import { Droplets, Waves, Users, Radio, ShieldCheck, LifeBuoy, Sparkles, Database, Bot, CloudRain, Thermometer, Wind, Gauge, Clock } from 'lucide-react';
import { FloodIntelligencePanel } from '../components/motion/FloodIntelligencePanel';
import { MultiHorizonForecastPanel } from '../components/motion/MultiHorizonForecastPanel';
import { RiskInterpretationCard } from '../components/ai/RiskInterpretationCard';
import { LiveIncidentFeed } from '../components/realtime/LiveIncidentFeed';
import { SituationAwarenessPanel } from '../components/operations/SituationAwarenessPanel';

export const DashboardPage: React.FC = () => {
  const {
    alerts,
    sosIncidents,
    aiPrediction,
    isAnalyzing,
    dashboardStats,
    currentWeather,
    isSimulationActive,
    triggerAIAnalysis,
    createSOSRequest,
    postGisLogs,
    liveIncidentFeed,
  } = useDisaster();

  const handleQuickSOS = () => {
    createSOSRequest({
      citizenName: 'Citizen Emergency Call',
      phone: '+1 (555) 911-0000',
      location: 'Downtown Basin Flood Line',
      coordinates: [13.083, 80.272],
      emergencyType: 'EVACUATION_NEEDED',
      peopleCount: 3,
      urgency: 'CRITICAL',
    });
  };

  return (
    <PageTransition className="p-6 space-y-6">
      {/* Top Banner & Quick SOS Action */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-gray-800">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
            Disaster Risk & Emergency Command Dashboard
            {isSimulationActive && (
              <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40">
                SIMULATION RUNNING
              </span>
            )}
          </h2>
          <p className="text-xs text-gray-400 font-mono mt-1">
            Real-Time Hydrological Sensor Feeds & PostGIS Spatial Analytics
          </p>
        </div>

        <EmergencySOSButton onClick={handleQuickSOS} size="md" />
      </div>

      {/* Grid Stats Counters */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        {/* Stat 1 */}
        <AnimatedCard delay={0.05} className="!p-4">
          <div className="flex items-center text-xs text-gray-400 mb-1">
            <Droplets className="w-4 h-4 mr-1.5 text-blue-400" />
            Rainfall Rate
          </div>
          <div className="text-2xl font-bold font-mono text-gray-100">
            <AnimatedCounter value={dashboardStats.rainfallMm} decimals={1} suffix=" mm" />
          </div>
          <div className="text-[10px] font-mono text-cyan-400 mt-1">+12% vs last hr</div>
        </AnimatedCard>

        {/* Stat 2 */}
        <AnimatedCard delay={0.1} className="!p-4">
          <div className="flex items-center text-xs text-gray-400 mb-1">
            <Waves className="w-4 h-4 mr-1.5 text-cyan-400" />
            Flood Risk
          </div>
          <div className="text-2xl font-bold font-mono text-gray-100">
            <AnimatedCounter value={dashboardStats.floodRiskPercent} suffix="%" />
          </div>
          <div className="text-[10px] font-mono text-rose-400 mt-1">High Risk Threshold</div>
        </AnimatedCard>

        {/* Stat 3 */}
        <AnimatedCard delay={0.15} className="!p-4">
          <div className="flex items-center text-xs text-gray-400 mb-1">
            <Users className="w-4 h-4 mr-1.5 text-amber-400" />
            Affected Pop.
          </div>
          <div className="text-2xl font-bold font-mono text-gray-100">
            <AnimatedCounter value={dashboardStats.affectedPopulation} />
          </div>
          <div className="text-[10px] font-mono text-gray-400 mt-1">Est. Direct Impact</div>
        </AnimatedCard>

        {/* Stat 4 */}
        <AnimatedCard delay={0.2} className="!p-4">
          <div className="flex items-center text-xs text-gray-400 mb-1">
            <Radio className="w-4 h-4 mr-1.5 text-rose-400" />
            Active SOS
          </div>
          <div className="text-2xl font-bold font-mono text-rose-400">
            <AnimatedCounter value={dashboardStats.activeSOSCount} />
          </div>
          <div className="text-[10px] font-mono text-rose-300 mt-1">Dispatch Required</div>
        </AnimatedCard>

        {/* Stat 5 */}
        <AnimatedCard delay={0.25} className="!p-4">
          <div className="flex items-center text-xs text-gray-400 mb-1">
            <ShieldCheck className="w-4 h-4 mr-1.5 text-emerald-400" />
            Shelters Open
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">
            <AnimatedCounter value={dashboardStats.availableShelters} />
          </div>
          <div className="text-[10px] font-mono text-emerald-300 mt-1">Ready for evacuees</div>
        </AnimatedCard>

        {/* Stat 6 */}
        <AnimatedCard delay={0.3} className="!p-4">
          <div className="flex items-center text-xs text-gray-400 mb-1">
            <LifeBuoy className="w-4 h-4 mr-1.5 text-indigo-400" />
            Rescue Teams
          </div>
          <div className="text-2xl font-bold font-mono text-indigo-300">
            <AnimatedCounter value={dashboardStats.rescueTeamsActive} />
          </div>
          <div className="text-[10px] font-mono text-gray-400 mt-1">Deployed in Field</div>
        </AnimatedCard>
      </div>

      {/* Live Meteorological & Rainfall Observation Feed (Priority 6) */}
      <div className="glass-panel p-5 rounded-2xl border border-gray-800 bg-gray-900/60 backdrop-blur-md">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-gray-800/80 pb-3 mb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <CloudRain className="w-5 h-5" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-sm font-bold font-mono text-gray-100 uppercase tracking-wide">
                  Live Meteorological Feed
                </h3>
                {/* Weather Source Badge */}
                {currentWeather?.source === 'real' && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    LIVE REAL DATA
                  </span>
                )}
                {currentWeather?.source === 'cached' && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                    CACHED (POSTGRESQL)
                  </span>
                )}
                {currentWeather?.source === 'simulation' && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
                    SIMULATION OVERRIDE
                  </span>
                )}
                {(!currentWeather?.source || currentWeather?.source === 'mock') && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-purple-500/20 text-purple-400 border border-purple-500/40">
                    SYNTHETIC SENSOR
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-400 font-mono mt-0.5">
                Station: {currentWeather?.location || 'Central Metro Basin'} • Coordinates: {currentWeather?.latitude?.toFixed(2) ?? '13.08'}°N, {currentWeather?.longitude?.toFixed(2) ?? '80.27'}°E
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono text-gray-400">
            <Clock className="w-3.5 h-3.5 text-gray-500" />
            <span>
              Observed:{' '}
              {currentWeather?.observed_at
                ? new Date(currentWeather.observed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                : 'Just now'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          <div className="p-2.5 rounded-xl bg-gray-950/40 border border-gray-800/60">
            <div className="text-[10px] font-mono text-gray-400 uppercase">Condition</div>
            <div className="text-sm font-bold text-gray-100 truncate mt-0.5">
              {currentWeather?.condition || 'Clear Sky'}
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-gray-950/40 border border-gray-800/60">
            <div className="text-[10px] font-mono text-gray-400 uppercase flex items-center gap-1">
              <Thermometer className="w-3 h-3 text-amber-400" /> Temp
            </div>
            <div className="text-sm font-bold font-mono text-gray-100 mt-0.5">
              {currentWeather?.temperature !== undefined ? `${currentWeather.temperature}°C` : '28.0°C'}
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-gray-950/40 border border-gray-800/60">
            <div className="text-[10px] font-mono text-gray-400 uppercase flex items-center gap-1">
              <Droplets className="w-3 h-3 text-cyan-400" /> Humidity
            </div>
            <div className="text-sm font-bold font-mono text-gray-100 mt-0.5">
              {currentWeather?.humidity !== undefined ? `${currentWeather.humidity}%` : '65%'}
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-gray-950/40 border border-gray-800/60">
            <div className="text-[10px] font-mono text-gray-400 uppercase flex items-center gap-1">
              <Wind className="w-3 h-3 text-teal-400" /> Wind Speed
            </div>
            <div className="text-sm font-bold font-mono text-gray-100 mt-0.5">
              {currentWeather?.wind_speed !== undefined ? `${currentWeather.wind_speed} km/h` : '10 km/h'}
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-gray-950/40 border border-gray-800/60">
            <div className="text-[10px] font-mono text-gray-400 uppercase flex items-center gap-1">
              <Gauge className="w-3 h-3 text-indigo-400" /> Pressure
            </div>
            <div className="text-sm font-bold font-mono text-gray-100 mt-0.5">
              {currentWeather?.pressure !== undefined ? `${currentWeather.pressure} hPa` : '1012 hPa'}
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-gray-950/40 border border-gray-800/60">
            <div className="text-[10px] font-mono text-gray-400 uppercase">Rain (1h)</div>
            <div className="text-sm font-bold font-mono text-blue-400 mt-0.5">
              {currentWeather?.rainfall_1h !== undefined ? `${currentWeather.rainfall_1h} mm` : '0.0 mm'}
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-gray-950/40 border border-gray-800/60">
            <div className="text-[10px] font-mono text-gray-400 uppercase">Rain (24h)</div>
            <div className="text-sm font-bold font-mono text-cyan-400 mt-0.5">
              {currentWeather?.rainfall_24h !== undefined ? `${currentWeather.rainfall_24h} mm` : '0.0 mm'}
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-gray-950/40 border border-gray-800/60">
            <div className="text-[10px] font-mono text-gray-400 uppercase">Precip Prob</div>
            <div className="text-sm font-bold font-mono text-violet-400 mt-0.5">
              {currentWeather?.precipitation_probability !== undefined ? `${currentWeather.precipitation_probability}%` : '0%'}
            </div>
          </div>
        </div>
        <div className="mt-3 pt-2.5 border-t border-gray-800/60 text-[10px] font-mono text-gray-500 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1">
          <span>* Real-time observations powered by Open-Meteo API (WMO Standards). Persisted & cached in PostgreSQL.</span>
          <span className="text-cyan-400/80">ML inference fed directly from live observations</span>
        </div>
      </div>

      {/* AI Prediction & Risk Score Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8">
          <AIPredictionPanel
            isAnalyzing={isAnalyzing}
            prediction={aiPrediction}
            onRunAnalysis={triggerAIAnalysis}
            isSimulationMode={isSimulationActive}
          />
        </div>

        <div className="lg:col-span-4 flex flex-col justify-between glass-panel p-6 rounded-2xl border border-gray-800">
          <h3 className="text-sm font-bold font-mono text-gray-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            GLOBAL COMMAND RISK SCORE
          </h3>

          <div className="my-auto py-4">
            <RiskScore
              score={aiPrediction ? aiPrediction.riskScore : 78}
              level={aiPrediction ? aiPrediction.riskLevel : 'HIGH'}
              size="lg"
            />
          </div>

          <div className="pt-4 border-t border-gray-800/80 text-[11px] font-mono text-gray-400 flex items-center justify-between">
            <span>PostGIS Query Latency</span>
            <span className="text-emerald-400 font-bold">14.2 ms</span>
          </div>
        </div>
      </div>

      {/* Phase 6: Situational Intelligence & Operational Awareness */}
      <SituationAwarenessPanel />

      {/* Phase 5.2: Advanced Flood Intelligence & Geospatial Inundation Analysis */}
      <MultiHorizonForecastPanel
        latitude={currentWeather?.latitude ?? 13.0827}
        longitude={currentWeather?.longitude ?? 80.2707}
        isSimulationMode={isSimulationActive}
      />

      <FloodIntelligencePanel
        latitude={currentWeather?.latitude ?? 13.0827}
        longitude={currentWeather?.longitude ?? 80.2707}
        isSimulationMode={isSimulationActive}
      />

      {/* AI Risk Interpretation & Prognosis Component */}
      <RiskInterpretationCard
        onOpenAssistant={() => {
          window.location.hash = '/ai-assistant';
        }}
      />

      {/* Real-Time Command Map & Live Feeds Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left GIS Command Map */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold font-mono text-gray-200 uppercase tracking-wider flex items-center gap-2">
              <Database className="w-4 h-4 text-blue-400" />
              GIS Disaster Map Overlay
            </h3>
            <span className="text-xs font-mono text-gray-400">PostGIS Geometry Layer</span>
          </div>
          <DisasterMap height="h-[520px]" />
        </div>

        {/* Right Active Emergency Alerts & Real-Time Incident Feed */}
        <div className="lg:col-span-5 space-y-5">
          {/* Live Incident Activity Stream */}
          <LiveIncidentFeed items={liveIncidentFeed} maxItems={6} />

          {/* Active Priority Alerts */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold font-mono text-gray-200 uppercase tracking-wider">
                Live Priority Alerts ({alerts.length})
              </h3>
              <span className="text-xs font-mono text-cyan-400">Auto-Synchronized</span>
            </div>

            <div className="max-h-[220px] overflow-y-auto pr-1">
              <StaggeredList className="space-y-2.5">
                {alerts.map((alert, idx) => (
                  <AlertCard key={alert.id} alert={alert} index={idx} />
                ))}
              </StaggeredList>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};
