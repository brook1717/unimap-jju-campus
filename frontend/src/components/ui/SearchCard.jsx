import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Search,
  MapPin,
  GraduationCap,
  UtensilsCrossed,
  BookOpen,
  Building2,
  DoorOpen,
  Wrench,
} from 'lucide-react';

const CHIPS = [
  { key: 'all',       icon: MapPin },
  { key: 'academic',  icon: GraduationCap },
  { key: 'dining',    icon: UtensilsCrossed },
  { key: 'library',   icon: BookOpen },
  { key: 'dormitory', icon: Building2 },
  { key: 'gate',      icon: DoorOpen },
  { key: 'facility',  icon: Wrench },
];

export default function SearchCard() {
  const { t } = useTranslation();
  const [activeChip, setActiveChip] = useState('all');

  return (
    <div
      className="
        absolute z-10
        bottom-0 left-0 right-0
        rounded-t-2xl
        md:bottom-auto md:top-4 md:left-4 md:right-auto
        md:w-96 md:rounded-xl
        bg-white shadow-lg
      "
    >
      {/* Mobile drag handle */}
      <div className="flex justify-center pt-2.5 pb-1 md:hidden">
        <span className="block h-1 w-10 rounded-full bg-slate-300" />
      </div>

      <div className="px-4 pt-2 pb-4 md:p-4">
        {/* Search input */}
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder={t('search_placeholder')}
            className="
              w-full rounded-lg bg-slate-50 py-2.5 pl-10 pr-4
              text-sm text-slate-900 placeholder:text-slate-400
              outline-none ring-1 ring-slate-200
              transition-shadow
              focus:ring-2 focus:ring-brand-primary/30
            "
          />
        </div>

        {/* Filter chips */}
        <div className="mt-3 flex gap-2 overflow-x-auto scrollbar-hide pb-0.5">
          {CHIPS.map(({ key, icon: Icon }) => {
            const active = activeChip === key;
            return (
              <button
                key={key}
                onClick={() => setActiveChip(key)}
                className={`
                  inline-flex shrink-0 items-center gap-1.5 rounded-full
                  px-3 py-1.5 text-xs font-medium
                  transition-colors
                  ${
                    active
                      ? 'bg-brand-primary text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }
                `}
              >
                <Icon className="h-3.5 w-3.5" />
                {t(key)}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
