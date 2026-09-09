import L from 'leaflet';

/**
 * Creates custom HTML Leaflet DivIcons with CSS hardware-accelerated keyframe pulses
 */
export const createAnimatedMarkerIcon = (
  type: 'DISASTER' | 'EMERGENCY' | 'SAFE_ZONE',
  title: string
): L.DivIcon => {
  let colorBg = 'bg-orange-500';
  let borderColor = 'border-orange-300';
  let pulseClass = 'marker-disaster';
  let iconSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>`;

  if (type === 'EMERGENCY') {
    colorBg = 'bg-rose-600';
    borderColor = 'border-rose-300';
    pulseClass = 'marker-emergency';
    iconSvg = `
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>`;
  } else if (type === 'SAFE_ZONE') {
    colorBg = 'bg-emerald-500';
    borderColor = 'border-emerald-200';
    pulseClass = 'marker-safe';
    iconSvg = `
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>`;
  }

  const html = `
    <div class="relative group flex items-center justify-center">
      <div class="${pulseClass} w-8 h-8 ${colorBg} border-2 ${borderColor} flex items-center justify-center shadow-lg transition-transform hover:scale-110">
        ${iconSvg}
      </div>
      <div class="absolute bottom-full mb-1 hidden group-hover:block bg-gray-900 text-gray-100 text-[11px] font-mono px-2 py-1 rounded shadow-xl whitespace-nowrap border border-gray-700 z-50 pointer-events-none">
        ${title}
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-animated-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};
