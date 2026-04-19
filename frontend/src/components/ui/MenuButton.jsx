import { Menu, X } from 'lucide-react';

export default function MenuButton({ isOpen, onClick }) {
  const Icon = isOpen ? X : Menu;

  return (
    <button
      onClick={onClick}
      aria-label="Toggle menu"
      className="
        absolute right-4 top-4 z-20
        flex h-11 w-11 items-center justify-center
        rounded-full bg-white shadow-md
        text-slate-700
        transition-all hover:bg-slate-50
        active:scale-95 active:bg-slate-100
        dark:bg-slate-800 dark:text-slate-200
        dark:shadow-slate-950/40
        dark:hover:bg-slate-700 dark:active:bg-slate-600
      "
    >
      <Icon className="h-5 w-5" />
    </button>
  );
}
