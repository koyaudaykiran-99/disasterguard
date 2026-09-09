import { SafetyStatus } from '../../types';

export const mockSafetyStatus: SafetyStatus = {
  score: 18,
  level: 'LOW',
  headline: 'LOW RISK',
  message: 'You are currently in a relatively safe area.',
  locationName: 'Guntur, Andhra Pradesh',
  updatedAt: '2 mins ago',
  factors: [
    {
      name: 'Precipitation Rate',
      value: '8.4 mm/hr (Light-Moderate)',
      status: 'SAFE',
    },
    {
      name: 'River Basin Clearance',
      value: '+1.8m below danger threshold',
      status: 'SAFE',
    },
    {
      name: 'Inundation Proximity',
      value: '3.6 km to nearest flood pocket',
      status: 'SAFE',
    },
    {
      name: 'Local Ground Elevation',
      value: '+22m above sea level (High Ground)',
      status: 'SAFE',
    },
  ],
};
