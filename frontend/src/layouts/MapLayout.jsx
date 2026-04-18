import { useState } from 'react';

import SearchCard from '../components/ui/SearchCard';
import MenuButton from '../components/ui/MenuButton';
import SideDrawer from '../components/ui/SideDrawer';

export default function MapLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-slate-100">
      {/* ── Map placeholder ────────────────────────────────────────────── */}
      {/*
        This div will be replaced by the Leaflet <MapContainer> in the
        next sprint.  For now it renders a subtle cross-hatch so the
        floating cards are visually testable.
      */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center select-none">
          <p className="text-6xl font-bold text-slate-200">UniMap</p>
          <p className="mt-1 text-sm tracking-wide text-slate-300">
            Map canvas will render here
          </p>
        </div>
      </div>

      {/* ── Floating UI layer ──────────────────────────────────────────── */}
      <SearchCard />
      <MenuButton
        isOpen={drawerOpen}
        onClick={() => setDrawerOpen((v) => !v)}
      />
      <SideDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}
