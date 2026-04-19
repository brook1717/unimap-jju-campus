import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { AnimatePresence, motion } from 'framer-motion';
import {
  X,
  Globe,
  Info,
  Image,
  Mail,
  ChevronRight,
  ArrowLeft,
  MapPin,
  ExternalLink,
  Moon,
  Sun,
} from 'lucide-react';
import useTheme from '../../hooks/useTheme';

/* ── Constants ────────────────────────────────────────────────────────── */

const LANGUAGES = [
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'am', label: 'AM', name: 'አማርኛ' },
  { code: 'so', label: 'SO', name: 'Soomaali' },
];

const MENU_ITEMS = [
  { key: 'about',   icon: Info,  view: 'about' },
  { key: 'gallery', icon: Image, view: 'gallery' },
  { key: 'contact', icon: Mail,  view: null },
];

const GALLERY_IMAGES = [
  { url: 'https://images.unsplash.com/photo-1562774053-701939374585?w=400&h=300&fit=crop&q=80', alt: 'University campus aerial view' },
  { url: 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=400&h=300&fit=crop&q=80', alt: 'Campus library building' },
  { url: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400&h=300&fit=crop&q=80', alt: 'Graduation day celebration' },
  { url: 'https://images.unsplash.com/photo-1607237138185-eedd9c632b0b?w=400&h=300&fit=crop&q=80', alt: 'Modern university building' },
  { url: 'https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=400&h=300&fit=crop&q=80', alt: 'Campus courtyard' },
  { url: 'https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0?w=400&h=300&fit=crop&q=80', alt: 'Students in lecture hall' },
  { url: 'https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=400&h=300&fit=crop&q=80', alt: 'Tree-lined campus walkway' },
  { url: 'https://images.unsplash.com/photo-1564981797816-1043664bf78d?w=400&h=300&fit=crop&q=80', alt: 'University architecture detail' },
];

const overlayVariants = {
  hidden:  { opacity: 0 },
  visible: { opacity: 1 },
};

const panelVariants = {
  hidden:  { x: '100%' },
  visible: { x: 0 },
};

const springTransition = { type: 'spring', damping: 26, stiffness: 300 };

/* ── Sub-views ────────────────────────────────────────────────────────── */

function MenuView({ t, i18n, switchLanguage, onNavigate, theme, toggleTheme }) {
  return (
    <div className="px-5 py-5">
      {/* Language toggle */}
      <div className="mb-6">
        <div className="mb-2.5 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
          <Globe className="h-3.5 w-3.5" />
          {t('language')}
        </div>

        <div className="flex gap-2">
          {LANGUAGES.map(({ code, label, name }) => {
            const active = i18n.language === code;
            return (
              <button
                key={code}
                onClick={() => switchLanguage(code)}
                className={`
                  flex flex-1 flex-col items-center gap-0.5
                  rounded-lg border px-3 py-2.5 min-h-[44px]
                  text-center transition-all active:scale-95
                  ${
                    active
                      ? 'border-brand-primary bg-brand-primary/5 text-brand-primary dark:bg-brand-primary/10'
                      : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
                  }
                `}
              >
                <span className="text-sm font-semibold">{label}</span>
                <span className="text-[11px] leading-tight">{name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Theme toggle */}
      <div className="mb-6">
        <div className="mb-2.5 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
          {theme === 'dark' ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
          {t('theme')}
        </div>
        <button
          onClick={toggleTheme}
          className="
            flex w-full items-center justify-between
            rounded-lg border border-slate-200 px-4 py-3 min-h-[44px]
            transition-all active:scale-[0.98]
            dark:border-slate-700 dark:bg-slate-800
          "
        >
          <span className="flex items-center gap-2.5 text-sm font-medium text-slate-700 dark:text-slate-200">
            {theme === 'dark' ? <Moon className="h-4 w-4 text-brand-primary" /> : <Sun className="h-4 w-4 text-amber-500" />}
            {theme === 'dark' ? t('dark_mode') : t('light_mode')}
          </span>
          {/* Toggle pill */}
          <div className={`relative h-6 w-11 rounded-full transition-colors ${theme === 'dark' ? 'bg-brand-primary' : 'bg-slate-300'}`}>
            <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform ${theme === 'dark' ? 'left-[22px]' : 'left-0.5'}`} />
          </div>
        </button>
      </div>

      <hr className="mb-5 border-slate-100 dark:border-slate-800" />

      {/* Menu items */}
      <nav className="space-y-1">
        {MENU_ITEMS.map(({ key, icon: Icon, view }) => (
          <button
            key={key}
            onClick={() => view && onNavigate(view)}
            className="
              flex w-full items-center gap-3
              rounded-lg px-3 py-2.5 min-h-[44px]
              text-left text-sm font-medium text-slate-700
              transition-all hover:bg-slate-50 active:scale-[0.98]
              dark:text-slate-200 dark:hover:bg-slate-800
            "
          >
            <Icon className="h-[18px] w-[18px] text-slate-400 dark:text-slate-500" />
            <span className="flex-1">{t(key)}</span>
            <ChevronRight className="h-4 w-4 text-slate-300 dark:text-slate-600" />
          </button>
        ))}
      </nav>
    </div>
  );
}

function AboutView({ t }) {
  return (
    <div className="px-5 py-5">
      {/* Logo + tagline */}
      <div className="mb-6 text-center">
        <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-brand-primary/10">
          <MapPin className="h-7 w-7 text-brand-primary" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">UniMap</h3>
        <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{t('app_tagline')}</p>
      </div>

      {/* Description */}
      <div className="mb-4 rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
        <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">
          {t('about_description')}
        </p>
      </div>

      {/* Developer card */}
      <div className="rounded-lg border border-slate-100 p-4 dark:border-slate-800">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
          {t('developer')}
        </p>
        <p className="text-sm font-semibold text-slate-900 dark:text-white">Biruk Kasahun</p>
        <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
          Cloud &amp; DevOps Engineer
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          AWS Certified Solutions Architect
        </p>

        <div className="mt-3 flex gap-2">
          <a
            href="#"
            className="
              inline-flex items-center gap-1.5 rounded-md
              bg-slate-50 px-3 py-1.5 min-h-[36px]
              text-xs font-medium text-slate-600
              transition-all hover:bg-slate-100 active:scale-95
              dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700
            "
          >
            <ExternalLink className="h-3 w-3" />
            Portfolio
          </a>
          <a
            href="#"
            className="
              inline-flex items-center gap-1.5 rounded-md
              bg-slate-50 px-3 py-1.5 min-h-[36px]
              text-xs font-medium text-slate-600
              transition-all hover:bg-slate-100 active:scale-95
              dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700
            "
          >
            <ExternalLink className="h-3 w-3" />
            GitHub
          </a>
        </div>
      </div>
    </div>
  );
}

function GalleryView({ t }) {
  return (
    <div className="px-5 py-5">
      <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">
        {t('app_tagline')} — Jigjiga University
      </p>

      <div className="grid grid-cols-2 gap-2">
        {GALLERY_IMAGES.map((img, i) => (
          <div
            key={i}
            className="overflow-hidden rounded-lg bg-slate-100 aspect-[4/3] dark:bg-slate-800"
          >
            <img
              src={img.url}
              alt={img.alt}
              loading="lazy"
              decoding="async"
              className="h-full w-full object-cover transition-transform duration-300 hover:scale-105"
            />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Main component ───────────────────────────────────────────────────── */

export default function SideDrawer({ isOpen, onClose }) {
  const { t, i18n } = useTranslation();
  const { theme, toggleTheme } = useTheme();
  const [view, setView] = useState('menu');

  // Reset to menu when drawer closes
  useEffect(() => {
    if (!isOpen) {
      const timer = setTimeout(() => setView('menu'), 300);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const switchLanguage = (code) => {
    i18n.changeLanguage(code);
    localStorage.setItem('unimap_lang', code);
  };

  const headerTitle =
    view === 'about'  ? t('about') :
    view === 'gallery' ? t('gallery') :
    t('menu');

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            key="overlay"
            variants={overlayVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 z-30 bg-black/40"
          />

          {/* Panel */}
          <motion.aside
            key="panel"
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
            transition={springTransition}
            className="
              fixed right-0 top-0 z-40
              flex h-full w-80 flex-col
              bg-white shadow-2xl
              dark:bg-slate-900 dark:shadow-slate-950/60
            "
          >
            {/* ── Header ──────────────────────────────────── */}
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4 dark:border-slate-800">
              {view !== 'menu' ? (
                <button
                  onClick={() => setView('menu')}
                  className="flex items-center gap-2 text-slate-500 transition-colors hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span className="text-base font-semibold text-slate-900 dark:text-white">
                    {headerTitle}
                  </span>
                </button>
              ) : (
                <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                  {headerTitle}
                </h2>
              )}

              <button
                onClick={onClose}
                aria-label={t('close')}
                className="
                  flex h-9 w-9 items-center justify-center
                  rounded-full text-slate-500
                  transition-all hover:bg-slate-100 active:scale-95
                  dark:text-slate-400 dark:hover:bg-slate-800
                "
              >
                <X className="h-4.5 w-4.5" />
              </button>
            </div>

            {/* ── Body (scrollable, animated) ────────────── */}
            <div className="flex-1 overflow-y-auto">
              <AnimatePresence mode="wait">
                <motion.div
                  key={view}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                >
                  {view === 'menu' && (
                    <MenuView
                      t={t}
                      i18n={i18n}
                      switchLanguage={switchLanguage}
                      onNavigate={setView}
                      theme={theme}
                      toggleTheme={toggleTheme}
                    />
                  )}
                  {view === 'about' && <AboutView t={t} />}
                  {view === 'gallery' && <GalleryView t={t} />}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* ── Footer ──────────────────────────────────── */}
            <div className="border-t border-slate-100 px-5 py-4 dark:border-slate-800">
              <p className="text-center text-xs text-slate-400 dark:text-slate-500">
                UniMap v0.1 &middot; Jigjiga University
              </p>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
