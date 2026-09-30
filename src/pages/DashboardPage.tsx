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
import { CommandCenterWeatherPanel } from '../components/weather/CommandCenterWeatherPanel';
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

      {/* Real-Time Meteorological & Rainfall Multi-Source Feed */}
      <CommandCenterWeatherPanel />

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
