# Citizen Map, Safe Corridors & Direction Guidance

## 1. Map Architecture
The Citizen Mobile App uses an interactive Leaflet GIS engine (\`CitizenMap.tsx\`) powered by OpenStreetMap standard tiles:
- Tile Layer URL: \`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png\`
- Attribution: \`&copy; OpenStreetMap contributors\`
- Map Lifecycle: Safe mount with container ref, \`invalidateSize()\` delayed trigger for PWA viewport stability, and clean teardown on route changes.

## 2. Layers & Indicators
- **User Location Pin**: High-contrast blue beacon with pulsing ambient radius and GPS accuracy circle.
- **Verified Relief Shelters**: Green shield markers with current occupancy, maximum capacity, and elevated terrain flags.
- **Emergency Medical Facilities**: Blue cross markers displaying emergency department ICU availability and distance.
- **Inundation Risk Zones**: Dashed red warning polygons marking high hazard zones (e.g. Downtown Riverside Basin, Northern Canal Lowlands) with depth in meters and localized warnings.
- **Active Distress Marker**: Prominent pulsing red beacon indicating citizen's own active SOS coordinates.
- **Safe Evacuation Polyline**: Emerald dashed corridor (\`#059669\`, \`dashArray: '8, 8'\`) routing towards the nearest elevated shelter, safely avoiding inundated basins.

## 3. Approximate Geographic Distance Standard
To strictly prevent misleading users during flood emergencies when roads may be impassable, all facility and routing distances are explicitly labeled:
\`"Approx. geographic distance"\` (e.g. \`~1.4 km (Approx. geographic distance)\`).
No fabricated street driving ETAs or turn-by-turn turn directions are displayed.

## 4. Touch & Interaction Design
- Minimum 48px touch targets for mobile accessibility.
- Filter Bar: All Facilities, Shelters, Hospitals, Flood Zones.
- "GPS Locate" button: Animates camera pan and zooms directly to device coordinates.
- Facility Card Tap: Immediately snaps map focus to the selected haven and redraws the safe evacuation line.
