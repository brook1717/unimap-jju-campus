import { useTranslation } from 'react-i18next';
import { AnimatePresence, motion } from 'framer-motion';
import {
  X,
  Globe,
  Info,
  Image,
  Mail,
  ChevronRight,
} from 'lucide-react';

const LANGUAGES = [
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'am', label: 'AM', name: 'አማርኛ' },
  { code: 'so', label: 'SO', name: 'Soomaali' },
];

const MENU_ITEMS = [
  { key: 'about',   icon: Info },
  { key: 'gallery', icon: Image },
  { key: 'contact', icon: Mail },
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

export default function SideDrawer({ isOpen, onClose }) {
  const { t, i18n } = useTranslation();

  const switchLanguage = (code) => {
    i18n.changeLanguage(code);
    localStorage.setItem('unimap_lang', code);
  };

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
            "
          >
            {/* ── Header ──────────────────────────────────── */}
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <h2 className="text-base font-semibold text-slate-900">
                {t('menu')}
              </h2>
              <button
                onClick={onClose}
                aria-label={t('close')}
                className="
                  flex h-8 w-8 items-center justify-center
                  rounded-full text-slate-500
                  transition-colors hover:bg-slate-100
                "
              >
                <X className="h-4.5 w-4.5" />
              </button>
            </div>

            {/* ── Body (scrollable) ───────────────────────── */}
            <div className="flex-1 overflow-y-auto px-5 py-5">
              {/* Language toggle */}
              <div className="mb-6">
                <div className="mb-2.5 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-400">
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
                          rounded-lg border px-3 py-2.5
                          text-center transition-colors
                          ${
                            active
                              ? 'border-brand-primary bg-brand-primary/5 text-brand-primary'
                              : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
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

              {/* Divider */}
              <hr className="mb-5 border-slate-100" />

              {/* Menu items */}
              <nav className="space-y-1">
                {MENU_ITEMS.map(({ key, icon: Icon }) => (
                  <button
                    key={key}
                    className="
                      flex w-full items-center gap-3
                      rounded-lg px-3 py-2.5
                      text-left text-sm font-medium text-slate-700
                      transition-colors hover:bg-slate-50
                    "
                  >
                    <Icon className="h-[18px] w-[18px] text-slate-400" />
                    <span className="flex-1">{t(key)}</span>
                    <ChevronRight className="h-4 w-4 text-slate-300" />
                  </button>
                ))}
              </nav>
            </div>

            {/* ── Footer ──────────────────────────────────── */}
            <div className="border-t border-slate-100 px-5 py-4">
              <p className="text-center text-xs text-slate-400">
                UniMap v0.1 &middot; Jigjiga University
              </p>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
