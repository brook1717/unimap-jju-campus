import { useState, useEffect, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  X,
  Loader2,
  MapPin,
  GraduationCap,
  UtensilsCrossed,
  BookOpen,
  Building2,
  DoorOpen,
  Wrench,
} from 'lucide-react';

import useDebounce from '../../hooks/useDebounce';
import useMediaQuery from '../../hooks/useMediaQuery';
import { fetchAutocomplete } from '../../services/api';

/* ── Constants ────────────────────────────────────────────────────────── */

const CHIPS = [
  { key: 'all',       icon: MapPin },
  { key: 'academic',  icon: GraduationCap },
  { key: 'dining',    icon: UtensilsCrossed },
  { key: 'library',   icon: BookOpen },
  { key: 'dormitory', icon: Building2 },
  { key: 'gate',      icon: DoorOpen },
  { key: 'facility',  icon: Wrench },
];

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

/* ── Component ────────────────────────────────────────────────────────── */

export default function SearchCard({ onLocationSelect }) {
  const { t } = useTranslation();
  const isDesktop = useMediaQuery('(min-width: 768px)');
  const inputRef = useRef(null);

  const [query, setQuery] = useState('');
  const [activeChip, setActiveChip] = useState('all');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const debouncedQuery = useDebounce(query, 300);

  /* ── Fetch autocomplete ─────────────────────────────────────────────── */
  useEffect(() => {
    const q = debouncedQuery.trim();
    if (!q) {
      setResults([]);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);

    fetchAutocomplete(q)
      .then(({ data }) => {
        if (!cancelled) setResults(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        if (!cancelled) setResults([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [debouncedQuery]);

  /* ── Handlers ───────────────────────────────────────────────────────── */
  const handleSelect = useCallback(
    (item) => {
      onLocationSelect?.(item.id);
      setQuery('');
      setResults([]);
      setExpanded(false);
      inputRef.current?.blur();
    },
    [onLocationSelect],
  );

  const handleClear = () => {
    setQuery('');
    setResults([]);
    inputRef.current?.focus();
  };

  const handleInputFocus = () => {
    if (!isDesktop) setExpanded(true);
  };

  const hasQuery = query.trim().length > 0;

  /* ── Shared sub-trees ───────────────────────────────────────────────── */

  const searchInput = (
    <div className="relative">
      {loading ? (
        <Loader2 className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-slate-400 dark:text-slate-500 animate-spin" />
      ) : (
        <Search className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-slate-400 dark:text-slate-500" />
      )}

      <input
        ref={inputRef}
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={handleInputFocus}
        placeholder={t('search_placeholder')}
        aria-label={t('search_buildings')}
        className="
          w-full rounded-lg bg-slate-50 py-2.5 pl-10 pr-10 min-h-[44px]
          text-sm text-slate-900 placeholder:text-slate-400
          outline-none ring-1 ring-slate-200
          transition-shadow
          focus:ring-2 focus:ring-brand-primary/30
          dark:bg-slate-800 dark:text-white dark:placeholder:text-slate-500
          dark:ring-slate-700 dark:focus:ring-brand-primary/40
        "
      />

      <AnimatePresence>
        {query && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={handleClear}
            aria-label={t('clear_search')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors dark:text-slate-500 dark:hover:text-slate-300"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );

  const filterChips = (
    <div className="mt-3 flex gap-2 overflow-x-auto scrollbar-hide pb-0.5">
      {CHIPS.map(({ key, icon: Icon }) => {
        const active = activeChip === key;
        return (
          <button
            key={key}
            onClick={() => setActiveChip(key)}
            className={`
              inline-flex shrink-0 items-center gap-1.5 rounded-full
              px-3 py-1.5 min-h-[36px] text-xs font-medium
              transition-all active:scale-95
              ${
                active
                  ? 'bg-brand-primary text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
              }
            `}
          >
            <Icon className="h-3.5 w-3.5" />
            {t(key)}
          </button>
        );
      })}
    </div>
  );

  const skeletonRows = (
    <div className="space-y-1 py-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center gap-3 px-3 py-2.5">
          <div className="h-8 w-8 shrink-0 rounded-full bg-slate-200 dark:bg-slate-700 animate-pulse" />
          <div className="flex-1 space-y-1.5">
            <div className="h-3.5 w-3/4 rounded bg-slate-200 dark:bg-slate-700 animate-pulse" />
            <div className="h-3 w-1/3 rounded bg-slate-200 dark:bg-slate-700 animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  );

  const resultsList = (
    <div className="border-t border-slate-100 dark:border-slate-800 mt-2 pt-1">
      {loading ? skeletonRows : results.length === 0 ? (
        <p className="py-8 text-center text-sm text-slate-400 dark:text-slate-500">
          {hasQuery ? t('no_results') : ''}
        </p>
      ) : (
        <div className="max-h-64 overflow-y-auto overscroll-contain md:max-h-72">
          {results.map((item) => (
            <button
              key={item.id}
              onClick={() => handleSelect(item)}
              className="
                flex w-full items-center gap-3 rounded-lg px-3 py-2.5 min-h-[44px]
                text-left transition-all hover:bg-slate-50 active:scale-[0.98]
                dark:hover:bg-slate-800
              "
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800 text-sm">
                {CATEGORY_EMOJI[item.category] || '📍'}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-900 dark:text-white">
                  {item.name}
                </p>
                <p className="text-xs capitalize text-slate-500 dark:text-slate-400">
                  {item.category}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );

  /* ── Desktop: static floating card ──────────────────────────────────── */
  if (isDesktop) {
    return (
      <div className="absolute z-10 top-4 left-4 w-96">
        <div className="bg-white rounded-xl shadow-lg p-4 dark:bg-slate-900 dark:shadow-slate-950/50">
          {searchInput}
          {filterChips}
          <AnimatePresence>
            {hasQuery && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                {resultsList}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    );
  }

  /* ── Mobile: animated bottom sheet ──────────────────────────────────── */
  return (
    <div className="fixed z-10 bottom-0 left-0 right-0">
      <motion.div
        className="bg-white rounded-t-2xl shadow-lg flex flex-col overflow-hidden dark:bg-slate-900 dark:shadow-slate-950/50"
        animate={expanded ? 'expanded' : 'collapsed'}
        variants={{
          collapsed: { height: 'auto' },
          expanded: { height: '65vh' },
        }}
        transition={{ type: 'spring', damping: 28, stiffness: 300 }}
      >
        {/* Drag handle — swipeable area */}
        <motion.div
          className="cursor-grab active:cursor-grabbing flex-shrink-0"
          drag="y"
          dragConstraints={{ top: 0, bottom: 0 }}
          dragElastic={0.15}
          onDragEnd={(_, { offset, velocity }) => {
            if (offset.y > 60 || velocity.y > 300) {
              setExpanded(false);
              inputRef.current?.blur();
            } else if (offset.y < -40 || velocity.y < -200) {
              setExpanded(true);
            }
          }}
        >
          <div className="flex justify-center pt-2.5 pb-1">
            <span className="block h-1 w-10 rounded-full bg-slate-300 dark:bg-slate-600" />
          </div>
        </motion.div>

        {/* Card body */}
        <div className="px-4 pt-2 pb-4 flex-1 flex flex-col min-h-0">
          {searchInput}
          {filterChips}

          {/* Results — scrollable independently from the sheet drag */}
          <AnimatePresence>
            {expanded && hasQuery && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 overflow-y-auto overscroll-contain min-h-0 mt-1"
              >
                {resultsList}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
