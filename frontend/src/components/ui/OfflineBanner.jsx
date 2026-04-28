import { AnimatePresence, motion } from 'framer-motion';
import { WifiOff } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function OfflineBanner({ isOffline }) {
  const { t } = useTranslation();

  return (
    <AnimatePresence>
      {isOffline && (
        <motion.div
          initial={{ y: -48, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -48, opacity: 0 }}
          transition={{ type: 'spring', damping: 24, stiffness: 300 }}
          role="status"
          aria-live="assertive"
          className="
            w-full z-50
            flex items-center justify-center gap-2
            bg-amber-500 px-4 py-2
            text-xs font-medium text-white shadow-md
            dark:bg-amber-600
          "
        >
          <WifiOff className="h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
          <span>{t('offline_banner')}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
