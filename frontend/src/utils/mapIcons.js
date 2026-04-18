import L from 'leaflet';

// ── Category → emoji lookup (one icon instance per category, cached) ─────────

const CATEGORY_EMOJI = {
  academic:  '🎓',
  office:    '🏢',
  library:   '📚',
  dormitory: '🏠',
  cafeteria: '🍽️',
  gate:      '🚪',
  facility:  '⚙️',
  lab:       '🔬',
};

const iconCache = {};

export function createCategoryIcon(category) {
  if (iconCache[category]) return iconCache[category];

  const emoji = CATEGORY_EMOJI[category] || '📍';
  const icon = L.divIcon({
    className: '',
    html: `<div class="campus-marker"><span>${emoji}</span></div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -22],
  });

  iconCache[category] = icon;
  return icon;
}

// ── Pulsing blue-dot icon for the user's GPS position ────────────────────────

export const userLocationIcon = L.divIcon({
  className: '',
  html: `
    <div class="user-marker">
      <span class="user-marker-ring"></span>
      <span class="user-marker-dot"></span>
    </div>
  `,
  iconSize: [22, 22],
  iconAnchor: [11, 11],
});
