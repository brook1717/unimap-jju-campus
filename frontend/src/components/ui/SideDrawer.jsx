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
  Users,
  Route,
  Database,
  Layers,
  Target,
  Smartphone,
} from 'lucide-react';
import useTheme from '../../hooks/useTheme';

/* ── Brand SVG icons (not in lucide-react) ─────────────────────────── */

const GithubIcon = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
    <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.009-.866-.013-1.7-2.782.603-3.369-1.342-3.369-1.342-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836a9.59 9.59 0 0 1 2.504.337c1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.161 22 16.416 22 12c0-5.523-4.477-10-10-10z" />
  </svg>
);

const LinkedinIcon = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
  </svg>
);

/* ── Constants ────────────────────────────────────────────────────────── */

const LANGUAGES = [
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'am', label: 'AM', name: 'አማርኛ' },
  { code: 'so', label: 'SO', name: 'Soomaali' },
];

const MENU_ITEMS = [
  { key: 'about',   icon: Info,  view: 'about' },
  { key: 'gallery', icon: Image, view: 'gallery' },
  { key: 'contact', icon: Mail,  view: 'contact' },
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
                aria-label={name}
                aria-pressed={i18n.language === code}
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
          aria-label={t('toggle_theme')}
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

function AboutView() {
  const TECH_FEATURES = [
    {
      icon: Route,
      title: 'A* Pathfinding Logic',
      desc: 'Processes a custom-built weighted graph of campus walkways to calculate the most efficient routes.',
    },
    {
      icon: Database,
      title: 'Geospatial Indexing',
      desc: 'Leveraging PostGIS for high-speed "Nearest Neighbor" searches to find the closest libraries, labs, or clinics instantly.',
    },
    {
      icon: Layers,
      title: 'Decoupled Architecture',
      desc: 'Built with a high-performance React frontend and a GeoDjango API, ensuring fluid, responsive navigation.',
    },
  ];

  const MISSION_ITEMS = [
    { icon: Target, text: 'Optimized Mobility — Eliminating the "search cost" of finding lecture halls and offices.' },
    { icon: MapPin, text: 'Unified Campus Truth — A single, verified source of data for all 120+ campus points of interest.' },
    { icon: Smartphone, text: 'PWA Accessibility — Designed as a Progressive Web App with offline-ready capabilities.' },
  ];

  const TEAM = [
    { name: 'Biruk Kasahun', role: 'Project Lead & Full-Stack Architect', focus: 'System lifecycle, Backend architecture, A* Logic, and AWS Cloud DevOps.' },
    { name: 'Bereket Gidi', role: 'Frontend Developer', focus: 'UI/UX implementation and PWA optimization.' },
    { name: 'Biruk Tamrat', role: 'GIS Data & QA Specialist', focus: 'Coordinate surveying and spatial data validation.' },
    { name: 'Absalew Alamirew', role: 'UI/UX Designer', focus: 'Iconography and accessibility refinements.' },
    { name: 'Hanan Yusuf', role: 'System Analyst', focus: 'Requirement engineering and stakeholder validation.' },
  ];

  return (
    <div className="px-5 py-5 space-y-5">
      {/* Header */}
      <section className="text-center">
        <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-brand-primary/10">
          <MapPin className="h-7 w-7 text-brand-primary" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">About UniMap</h3>
        <p className="mt-1 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
          An intelligent geospatial platform engineered to navigate the spatial complexities
          of the Jigjiga University campus.
        </p>
        <p className="mt-2 text-xs text-slate-400 dark:text-slate-500">
          Software Engineering Capstone Project
        </p>
      </section>

      {/* The Intelligence Behind the Map */}
      <section>
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
          The Intelligence Behind the Map
        </h4>
        <div className="space-y-2.5">
          {TECH_FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="rounded-lg bg-slate-50 p-3.5 dark:bg-slate-800">
              <div className="mb-1.5 flex items-center gap-2">
                <Icon className="h-4 w-4 text-brand-primary" />
                <span className="text-sm font-semibold text-slate-800 dark:text-slate-100">{title}</span>
              </div>
              <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-400">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Core Mission */}
      <section>
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
          Core Mission
        </h4>
        <ul className="space-y-2">
          {MISSION_ITEMS.map(({ icon: Icon, text }) => (
            <li key={text} className="flex gap-2.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
              <Icon className="mt-0.5 h-3.5 w-3.5 flex-shrink-0 text-brand-primary" />
              <span>{text}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Development Team */}
      <section>
        <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
          <Users className="h-3.5 w-3.5" />
          The Development Team
        </h4>
        <div className="space-y-2">
          {TEAM.map(({ name, role, focus }) => (
            <div key={name} className="rounded-lg border border-slate-100 p-3 dark:border-slate-800">
              <p className="text-sm font-semibold text-slate-900 dark:text-white">{name}</p>
              <p className="text-xs font-medium text-brand-primary">{role}</p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{focus}</p>
            </div>
          ))}
        </div>
      </section>
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

function ContactView() {
  const LINKS = [
    {
      icon: Mail,
      label: 'Email',
      value: 'brookkasahun@gmail.com',
      href: 'mailto:brookkasahun@gmail.com',
    },
    {
      icon: LinkedinIcon,
      label: 'LinkedIn',
      value: 'biruk-kasahun',
      href: 'https://www.linkedin.com/in/biruk-kasahun-684b682a6',
    },
    {
      icon: Globe,
      label: 'Portfolio',
      value: 'birukkasahun.com',
      href: 'https://birukkasahun.com/',
    },
    {
      icon: GithubIcon,
      label: 'GitHub',
      value: 'brook1717',
      href: 'https://github.com/brook1717',
    },
  ];

  return (
    <div className="px-5 py-5 space-y-5">
      {/* Header */}
      <section className="text-center">
        <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-brand-primary/10">
          <Mail className="h-7 w-7 text-brand-primary" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">Contact</h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Get in touch with the project lead.
        </p>
      </section>

      {/* Project Lead card */}
      <section className="rounded-lg border border-slate-100 p-4 dark:border-slate-800">
        <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
          Project Lead
        </p>
        <p className="text-base font-bold text-slate-900 dark:text-white">Biruk Kasahun</p>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Full-Stack Architect &amp; Cloud DevOps Engineer
        </p>
      </section>

      {/* Contact links */}
      <section className="space-y-2">
        {LINKS.map(({ icon: Icon, label, value, href }) => (
          <a
            key={label}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="
              flex items-center gap-3 rounded-lg
              border border-slate-100 px-4 py-3 min-h-[48px]
              transition-all hover:bg-slate-50 active:scale-[0.98]
              dark:border-slate-800 dark:hover:bg-slate-800
            "
          >
            <Icon className="h-4.5 w-4.5 text-brand-primary flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-xs text-slate-400 dark:text-slate-500">{label}</p>
              <p className="truncate text-sm font-medium text-slate-700 dark:text-slate-200">
                {value}
              </p>
            </div>
            <ExternalLink className="h-3.5 w-3.5 text-slate-300 dark:text-slate-600 flex-shrink-0" />
          </a>
        ))}
      </section>
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
    view === 'about'   ? t('about') :
    view === 'gallery' ? t('gallery') :
    view === 'contact' ? t('contact') :
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
                  aria-label={t('back')}
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
                  {view === 'about' && <AboutView />}
                  {view === 'gallery' && <GalleryView t={t} />}
                  {view === 'contact' && <ContactView />}
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
