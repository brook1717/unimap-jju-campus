import { motion } from 'framer-motion';
import { X, Navigation } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import useMediaQuery from '../../hooks/useMediaQuery';

/* ── Helpers ──────────────────────────────────────────────────────────── */

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

const PLACEHOLDER_IMG =
  'https://images.unsplash.com/photo-1562774053-701939374585?w=600&h=300&fit=crop&q=80';

/* ── Component ────────────────────────────────────────────────────────── */

export default function LocationDetailsCard({ location, onClose, onDirections }) {
  const { t } = useTranslation();
  const isDesktop = useMediaQuery('(min-width: 768px)');

  if (!location) return null;

  const { name, category, description, photo } = location.properties;
  const imageUrl = photo || PLACEHOLDER_IMG;
  const emoji = CATEGORY_EMOJI[category] || '📍';

  /* ── Shared card content ──────────────────────────────────────────── */
  const cardContent = (
    <>
      {/* Close button — floats over image */}
      <button
        onClick={onClose}
        className="
          absolute top-3 right-3 z-10
          flex h-8 w-8 items-center justify-center
          rounded-full bg-white/80 backdrop-blur
          text-slate-600 shadow-sm
          transition-colors hover:bg-white
        "
        aria-label={t('close')}
      >
        <X className="h-4 w-4" />
      </button>

      {/* Image */}
      <div className="relative h-44 bg-slate-200">
        <img
          src={imageUrl}
          alt={name}
          className="h-full w-full object-cover"
          loading="lazy"
          decoding="async"
        />
        {/* Category badge */}
        <div className="absolute bottom-2 left-3 flex items-center gap-1.5 rounded-full bg-white/90 backdrop-blur px-2.5 py-1 text-xs font-medium text-slate-700 shadow-sm">
          <span>{emoji}</span>
          <span className="capitalize">{category}</span>
        </div>
      </div>

      {/* Body */}
      <div className="p-4">
        <h3 className="text-lg font-bold text-slate-900 leading-snug">
          {name}
        </h3>

        {description && (
          <p className="mt-2 text-sm text-slate-500 leading-relaxed line-clamp-3">
            {description}
          </p>
        )}

        {/* CTA */}
        <button
          onClick={() => onDirections?.(location)}
          className="
            mt-4 flex w-full items-center justify-center gap-2
            rounded-lg bg-brand-primary py-3 px-4
            text-sm font-semibold text-white
            shadow-md
            transition-all
            hover:bg-brand-primary/90 hover:shadow-lg
            active:scale-[0.98]
          "
        >
          <Navigation className="h-4 w-4" />
          {t('directions_to_here')}
        </button>
      </div>
    </>
  );

  /* ── Desktop: floating card ──────────────────────────────────────── */
  if (isDesktop) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="absolute z-10 top-4 left-4 w-96"
      >
        <div className="relative overflow-hidden rounded-xl bg-white shadow-lg">
          {cardContent}
        </div>
      </motion.div>
    );
  }

  /* ── Mobile: bottom sheet ────────────────────────────────────────── */
  return (
    <motion.div
      initial={{ y: '100%' }}
      animate={{ y: 0 }}
      exit={{ y: '100%' }}
      transition={{ type: 'spring', damping: 28, stiffness: 300 }}
      className="fixed z-10 bottom-0 left-0 right-0"
    >
      <div className="relative max-h-[80vh] overflow-hidden overflow-y-auto overscroll-contain rounded-t-2xl bg-white shadow-lg">
        {/* Drag handle */}
        <div className="sticky top-0 z-10 flex justify-center bg-white pt-2.5 pb-1">
          <span className="block h-1 w-10 rounded-full bg-slate-300" />
        </div>
        {cardContent}
      </div>
    </motion.div>
  );
}
