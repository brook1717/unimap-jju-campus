import L from 'leaflet';

// ── Category → emoji lookup (one icon instance per category, cached) ─────────

const CATEGORY_EMOJI = {
  academic:         '🎓',
  administrative:   '🏛️',
  cafeteria:        '�️',
  campus_facility:  '🏗️',
  classroom:        '�',
  college:          '🏫',
  dining:           '🍽️',
  dormitory:        '🏠',
  facility:         '⚙️',
  gate:             '🚪',
  lab:              '🔬',
  lecture_hall:      '🎤',
  library:          '📚',
  office:           '🏢',
  recreation:       '🌳',
  student_services: '🏥',
  utility:          '�',
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

// ── Label icon (emoji + name below) — shown at high zoom ─────────────────────

const labelCache = {};

export function createLabelIcon(category, name) {
  const key = `${category}::${name}`;
  if (labelCache[key]) return labelCache[key];

  const emoji = CATEGORY_EMOJI[category] || '📍';
  const escapedName = name.replace(/"/g, '&quot;').replace(/</g, '&lt;');

  const icon = L.divIcon({
    className: '',
    html: `
      <div class="campus-marker-labelled">
        <div class="campus-marker"><span>${emoji}</span></div>
        <span class="campus-marker-label">${escapedName}</span>
      </div>`,
    iconSize: [36, 50],
    iconAnchor: [18, 18],
    popupAnchor: [0, -22],
  });

  labelCache[key] = icon;
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
