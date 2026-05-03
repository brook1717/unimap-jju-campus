import { useState, useEffect } from 'react';
import { X, Download } from 'lucide-react';

const STORAGE_KEY = 'unimap_banner_dismissed';

/**
 * Checks if the current browser is a mobile user-agent AND not already
 * running as an installed PWA / TWA (standalone display mode).
 */
function shouldShow() {
  if (typeof window === 'undefined') return false;

  // Already dismissed
  try {
    if (localStorage.getItem(STORAGE_KEY) === '1') return false;
  } catch {
    return false;
  }

  // Running as installed PWA/TWA — don't show
  const isStandalone =
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true;
  if (isStandalone) return false;

  // Mobile UA check
  const ua = navigator.userAgent || '';
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
  return isMobile;
}

export default function AppInstallBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Delay slightly so it doesn't flash during page load
    const timer = setTimeout(() => setVisible(shouldShow()), 1500);
    return () => clearTimeout(timer);
  }, []);

  if (!visible) return null;

  const dismiss = () => {
    setVisible(false);
    try {
      localStorage.setItem(STORAGE_KEY, '1');
    } catch {
      /* storage full — silently ignore */
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 safe-area-pb animate-slide-up">
      <div
        className="
          mx-3 mb-3 flex items-center gap-3
          rounded-2xl border border-slate-200 bg-white/95 px-4 py-3
          shadow-lg backdrop-blur-sm
          dark:border-slate-700 dark:bg-slate-900/95
        "
      >
        {/* App icon */}
        <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-brand-primary">
          <span className="text-lg text-white" aria-hidden="true">🗺️</span>
        </div>

        {/* Text */}
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-slate-900 dark:text-white">
            Get UniMap on Google Play
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            For the best campus experience
          </p>
        </div>

        {/* CTA button */}
        <a
          href="https://play.google.com/store/apps/details?id=com.birukkasahun.unimap"
          target="_blank"
          rel="noopener noreferrer"
          className="
            flex items-center gap-1.5 rounded-lg
            bg-brand-primary px-3 py-2
            text-xs font-semibold text-white
            transition-all active:scale-95
          "
        >
          <Download className="h-3.5 w-3.5" />
          Install
        </a>

        {/* Close */}
        <button
          onClick={dismiss}
          aria-label="Dismiss install banner"
          className="
            flex h-7 w-7 flex-shrink-0 items-center justify-center
            rounded-full text-slate-400 transition-colors
            hover:bg-slate-100 hover:text-slate-600
            dark:hover:bg-slate-800 dark:hover:text-slate-300
          "
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
