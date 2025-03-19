'use client';

import { Menu, PanelLeft, PanelLeftClose } from 'lucide-react';

import React from 'react';

import { Separator } from '@/components/ui/separator';

import { cn } from '@/lib/utils';

export default function Topbar({ branding }) {
  return (
    <div className="topbar">
      <div id="mobile-menu-button-portal" />
      {/* Separator */}
      <Separator orientation="vertical" className="separator" />

      <div className="topbar-content">
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* Mobile branding */}
          <div className="branding-container">
            <img
              className="branding-logo"
              src={`${branding?.logo}?timstamp=${new Date().getTime()}`}
              alt={branding?.name}
            />
            <span className="branding-name">{branding?.name}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
