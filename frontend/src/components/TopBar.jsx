'use client';

import { Bars3Icon } from '@heroicons/react/24/outline';

export default function Topbar({ setSidebarOpen, branding }) {
  return (
    <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
      <button type="button" className="-m-2.5 p-2.5 text-gray-700 lg:hidden" onClick={() => setSidebarOpen(true)}>
        <span className="sr-only">Open sidebar</span>
        <Bars3Icon className="h-6 w-6" aria-hidden="true" />
      </button>

      {/* Separator */}
      <div className="h-6 w-px bg-gray-200 lg:hidden" aria-hidden="true" />

      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* Mobile branding */}
          <div className="flex lg:hidden">
            <img
              className="h-8 w-8"
              src={branding.logo}
              alt={branding.name}
            />
            <span className="ml-3 text-lg font-semibold text-gray-900">{branding.name}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
