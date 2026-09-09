import { Alert } from '../../types';

export const mockAlerts: Alert[] = [
  {
    id: 'alert-01',
    title: 'Heavy rainfall detected in your area',
    severity: 'MODERATE',
    category: 'RAINFALL',
    location: 'Guntur Metro & Krishna Basin',
    description: 'Doppler radar indicates concentrated squall lines moving East-Northeast. 25–40mm accumulation expected within 3 hours. Local lowlands may experience transient water accumulation.',
    timestamp: '2026-09-07T14:30:00Z',
    timeAgo: 'Updated 4 min ago',
    instructions: [
      'Avoid driving through low-lying subterranean passes',
      'Keep communications battery banks charged',
      'Review nearest safe shelter locations in the app',
    ],
  },
  {
    id: 'alert-02',
    title: 'Flash Flood Watch for Lowland Channels',
    severity: 'HIGH',
    category: 'FLOOD',
    location: 'Eastern Canal Inundation Sector',
    description: 'Upstream barrage release combined with ongoing precipitation has elevated canal water velocity. Lowland residents should stay alert to siren warnings.',
    timestamp: '2026-09-07T13:45:00Z',
    timeAgo: 'Updated 45 min ago',
    instructions: [
      'Relocate livestock and valuables to elevated floors',
      'Do not walk or drive across flooded culverts',
      'Keep emergency radio tuned to 104.2 MHz Disaster Relay',
    ],
  },
  {
    id: 'alert-03',
    title: 'Coastal Wind & Tidal Surge Advisory',
    severity: 'LOW',
    category: 'CYCLONE',
    location: 'Coastal Andhra Belt (50km East)',
    description: 'Sustained offshore winds reaching 45–55 km/h. Fishermen advised not to venture into deep sea. Coastal embankments currently stable.',
    timestamp: '2026-09-07T12:00:00Z',
    timeAgo: 'Updated 2 hr ago',
    instructions: [
      'Secure loose outdoor roofing and solar panels',
      'Maintain adequate drinking water storage',
    ],
  },
];
