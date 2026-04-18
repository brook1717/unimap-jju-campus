import { useState, useEffect, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Search,
  Loader2,
  ArrowUpDown,
  LocateFixed,
  Footprints,
  Clock,
  AlertTriangle,
} from 'lucide-react';

import useDebounce from '../../hooks/useDebounce';
import useMediaQuery from '../../hooks/useMediaQuery';
import {
  fetchAutocomplete,
  fetchDirections,
  fetchNearestLocation,
} from '../../services/api';

/* ── Helpers ──────────────────────────────────────────────────────────── */

const CATEGORY_EMOJI = {
  academic: '🎓', office: '🏢', library: '📚', dormitory: '🏠',
  cafeteria: '🍽️', gate: '🚪', facility: '⚙️', lab: '🔬',
};

const fmtDist = (m) => (m < 1000 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(1)} km`);
const fmtTime = (min) => (min < 1 ? '< 1 min' : `~${Math.round(min)} min`);

/* ── Component ────────────────────────────────────────────────────────── */

export default function NavigationCard({
  destination,
  userPosition,
  onRouteReady,
  onCancel,
}) {
  const { t } = useTranslation();
  const isDesktop = useMediaQuery('(min-width: 768px)');
  const inputRef = useRef(null);

  /* ── Points ───────────────────────────────────────────────────────── */
  const [startMode, setStartMode] = useState(userPosition ? 'gps' : 'search');
  const [startLoc, setStartLoc] = useState(null);
  const [endLoc] = useState(
    destination
      ? { id: destination.id, name: destination.properties.name }
      : null,
  );

  /* ── Start search ─────────────────────────────────────────────────── */
  const [startQuery, setStartQuery] = useState('');
  const [startResults, setStartResults] = useState([]);
  const [searchingStart, setSearchingStart] = useState(false);
  const debouncedStart = useDebounce(startQuery, 300);

  /* ── Route ────────────────────────────────────────────────────────── */
  const [routeData, setRouteData] = useState(null);
  const [routeLoading, setRouteLoading] = useState(false);
  const [routeError, setRouteError] = useState(null);
  const [resolvingGps, setResolvingGps] = useState(false);

  /* ── Resolve GPS → nearest campus location ────────────────────────── */
  useEffect(() => {
    if (startMode !== 'gps' || !userPosition) return;
    let cancelled = false;
    setResolvingGps(true);

    fetchNearestLocation(userPosition[0], userPosition[1])
      .then(({ data }) => {
        if (cancelled) return;
        const feat = data?.features?.[0] ?? data;
        if (feat?.id) {
          setStartLoc({
            id: feat.id,
            name: feat.properties?.name ?? t('my_location'),
          });
        }
      })
      .catch(() => {
        if (!cancelled) setStartMode('search');
      })
      .finally(() => {
        if (!cancelled) setResolvingGps(false);
      });

    return () => { cancelled = true; };
  }, [startMode, userPosition, t]);

  /* ── Start autocomplete ───────────────────────────────────────────── */
  useEffect(() => {
    if (startMode !== 'search') return;
    const q = debouncedStart.trim();
    if (!q) { setStartResults([]); setSearchingStart(false); return; }
    let cancelled = false;
    setSearchingStart(true);
    fetchAutocomplete(q)
      .then(({ data }) => { if (!cancelled) setStartResults(Array.isArray(data) ? data : []); })
      .catch(() => { if (!cancelled) setStartResults([]); })
      .finally(() => { if (!cancelled) setSearchingStart(false); });
    return () => { cancelled = true; };
  }, [debouncedStart, startMode]);

  /* ── Fetch route when both points are ready ───────────────────────── */
  useEffect(() => {
    if (!startLoc?.id || !endLoc?.id) return;
    if (startLoc.id === endLoc.id) return;

    let cancelled = false;
    setRouteLoading(true);
    setRouteError(null);

    fetchDirections(startLoc.id, endLoc.id)
      .then(({ data }) => {
        if (cancelled) return;
        setRouteData(data);
        onRouteReady?.(data);
      })
      .catch((err) => {
        if (cancelled) return;
        const msg = err.response?.data?.message ?? t('no_path_found');
        setRouteError(msg);
        onRouteReady?.(null);
      })
      .finally(() => {
        if (!cancelled) setRouteLoading(false);
      });

    return () => { cancelled = true; };
  }, [startLoc?.id, endLoc?.id, onRouteReady, t]);

  /* ── Handlers ─────────────────────────────────────────────────────── */
  const handleStartSelect = useCallback((item) => {
    setStartLoc({ id: item.id, name: item.name });
    setStartMode('selected');
    setStartQuery('');
    setStartResults([]);
  }, []);

  const openStartSearch = useCallback(() => {
    setStartMode('search');
    setStartLoc(null);
    setRouteData(null);
    setRouteError(null);
    onRouteReady?.(null);
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [onRouteReady]);

  const useMyLocation = useCallback(() => {
    setStartMode('gps');
    setStartLoc(null);
    setStartQuery('');
    setStartResults([]);
    setRouteData(null);
    setRouteError(null);
    onRouteReady?.(null);
  }, [onRouteReady]);

  const handleSwap = useCallback(() => {
    if (!startLoc || !endLoc) return;
    // Swap is visual only; full swap requires lifting endLoc state
  }, [startLoc, endLoc]);

  /* ── Sub-trees ────────────────────────────────────────────────────── */

  const startField = (
    <div className="flex items-center gap-3">
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-500">
        <span className="block h-2 w-2 rounded-full bg-white" />
      </span>
      {startMode === 'search' ? (
        <div className="relative flex-1">
          {searchingStart ? (
            <Loader2 className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-slate-400" />
          ) : (
            <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          )}
          <input
            ref={inputRef}
            type="text"
            value={startQuery}
            onChange={(e) => setStartQuery(e.target.value)}
            placeholder={t('search_start')}
            className="
              w-full rounded-md bg-slate-50 py-2 pl-9 pr-3
              text-sm text-slate-900 placeholder:text-slate-400
              outline-none ring-1 ring-slate-200
              focus:ring-2 focus:ring-brand-primary/30
            "
          />
        </div>
      ) : (
        <button
          onClick={openStartSearch}
          className="flex-1 truncate rounded-md bg-slate-50 px-3 py-2 text-left text-sm text-slate-700 ring-1 ring-slate-200 transition-colors hover:bg-slate-100"
        >
          {resolvingGps ? (
            <span className="flex items-center gap-2 text-slate-400">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              {t('calculating_route')}
            </span>
          ) : startLoc ? (
            <span className="flex items-center gap-2">
              {startMode === 'gps' && <LocateFixed className="h-3.5 w-3.5 text-emerald-500" />}
              {startLoc.name}
            </span>
          ) : (
            <span className="text-slate-400">{t('search_start')}</span>
          )}
        </button>
      )}
    </div>
  );

  const endField = (
    <div className="flex items-center gap-3">
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-primary">
        <span className="block h-2 w-2 rounded-full bg-white" />
      </span>
      <div className="flex-1 truncate rounded-md bg-slate-50 px-3 py-2 text-sm font-medium text-slate-900 ring-1 ring-slate-200">
        {endLoc?.name ?? '—'}
      </div>
    </div>
  );

  const searchResults = startMode === 'search' && startQuery.trim() && (
    <div className="mt-1 max-h-48 overflow-y-auto overscroll-contain border-t border-slate-100 pt-1">
      {startResults.length === 0 && !searchingStart ? (
        <p className="py-4 text-center text-xs text-slate-400">{t('no_results')}</p>
      ) : (
        startResults.map((item) => (
          <button
            key={item.id}
            onClick={() => handleStartSelect(item)}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors hover:bg-slate-50"
          >
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs">
              {CATEGORY_EMOJI[item.category] || '📍'}
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-900">{item.name}</p>
              <p className="text-xs capitalize text-slate-500">{item.category}</p>
            </div>
          </button>
        ))
      )}
    </div>
  );

  const gpsButton = startMode === 'search' && userPosition && (
    <button
      onClick={useMyLocation}
      className="mt-1 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-emerald-600 transition-colors hover:bg-emerald-50"
    >
      <LocateFixed className="h-4 w-4" />
      {t('my_location')}
    </button>
  );

  const journeySummary = routeData?.properties && (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      className="mt-3 flex items-center justify-center gap-6 rounded-lg bg-brand-primary/5 px-4 py-3"
    >
      <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
        <Footprints className="h-4 w-4 text-brand-primary" />
        {fmtDist(routeData.properties.total_distance_m)}
      </div>
      <div className="h-4 w-px bg-slate-200" />
      <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
        <Clock className="h-4 w-4 text-brand-primary" />
        {fmtTime(routeData.properties.estimated_walking_time_min)}
      </div>
    </motion.div>
  );

  const errorAlert = routeError && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mt-3 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5"
    >
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
      <p className="text-sm text-red-700">{routeError}</p>
    </motion.div>
  );

  const loadingBar = routeLoading && (
    <div className="mt-3 flex items-center justify-center gap-2 py-2 text-sm text-slate-400">
      <Loader2 className="h-4 w-4 animate-spin" />
      {t('calculating_route')}
    </div>
  );

  /* ── Card content ─────────────────────────────────────────────────── */
  const cardBody = (
    <div className="p-4">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">{t('navigation')}</h3>
        <button
          onClick={onCancel}
          className="flex h-7 w-7 items-center justify-center rounded-full text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
          aria-label={t('close')}
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Start / End fields with swap */}
      <div className="relative">
        {startField}

        {/* Connector line + swap */}
        <div className="my-1.5 ml-[11px] flex items-center gap-2">
          <div className="h-4 w-px border-l border-dashed border-slate-300" />
          <button
            onClick={handleSwap}
            title={t('swap_points')}
            className="flex h-6 w-6 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-400 transition-colors hover:bg-slate-50 hover:text-slate-600"
          >
            <ArrowUpDown className="h-3 w-3" />
          </button>
        </div>

        {endField}
      </div>

      {/* GPS shortcut */}
      {gpsButton}

      {/* Search results */}
      {searchResults}

      {/* Route state */}
      {loadingBar}
      {errorAlert}
      {journeySummary}

      {/* Cancel */}
      <button
        onClick={onCancel}
        className="
          mt-4 w-full rounded-lg border border-slate-200
          py-2.5 text-sm font-medium text-slate-600
          transition-colors hover:bg-slate-50
        "
      >
        {t('cancel_nav')}
      </button>
    </div>
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
        <div className="overflow-hidden rounded-xl bg-white shadow-lg">
          {cardBody}
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
      <div className="max-h-[85vh] overflow-y-auto overscroll-contain rounded-t-2xl bg-white shadow-lg">
        <div className="sticky top-0 z-10 flex justify-center bg-white pt-2.5 pb-1">
          <span className="block h-1 w-10 rounded-full bg-slate-300" />
        </div>
        {cardBody}
      </div>
    </motion.div>
  );
}
