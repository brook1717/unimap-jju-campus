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
        transition-colors hover:bg-slate-50 active:bg-slate-100
      "
    >
      <Icon className="h-5 w-5" />
    </button>
  );
}
