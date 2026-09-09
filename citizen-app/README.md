# AI-DisasterGuard — Citizen / User Mobile Web Application

> **Predict Early. Warn Faster. Respond Smarter.**

The Citizen/User Application provides an emergency safety mobile interface designed for citizens during extreme weather and flood events.

---

## Features (Phase 1 Foundation)

* **Hero Safety Status Experience**: Animated circular risk gauge displaying current threat level (0–100) with spring physics and context narrative.
* **4-Tier Dynamic Risk Language**: Seamless visual identity adapting across `LOW` (calm emerald), `MODERATE` (amber warning), `HIGH` (orange alert), and `CRITICAL` (crimson emergency).
* **Tactile Emergency SOS Trigger**: Large, breathing halo emergency button with tactile press feedback and 1-tap accessibility.
* **Emergency Quick Actions**:
  * **Safe Map**: Verified high-ground corridors avoiding flooded river basins.
  * **Shelters**: Real-time capacity, elevation, and food/water/medical inventory.
  * **Hospitals**: Nearby emergency departments and trauma centers.
  * **Alerts**: Real-time disaster broadcasts and actionable safety instructions.
* **Communication Resilience Status**: Transparent indicator displaying Internet, GPS, and Emergency Relay readiness.
* **72-Hour Evacuation Go-Bag**: Interactive readiness checklist for citizen households.
* **PWA Foundation**: Web App Manifest, Service Worker caching foundation, responsive mobile shell (360px–430px) with desktop framing.

---

## Development

```bash
# Install dependencies
npm install

# Start Vite dev server on port 3001
npm run dev

# Build for production
npm run build
```

The Command Centre runs concurrently on port `3000`, while the Citizen App runs on port `3001`.
