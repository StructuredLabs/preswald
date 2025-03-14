'use client';

import { Menu, PanelLeft, PanelLeftClose } from 'lucide-react';

import React from 'react';

import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

import { cn } from '@/lib/utils';

const TopbarWidget = ({
  branding = window.PRESWALD_BRANDING, // default to PRESWALD_BRANDING if nothing is passed
}) => {
  return (
    <div className="fixed top-0 left-0 right-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b bg-background -mx-8 sm:-mx-10 lg:-mx-12 shadow-sm  w-fill">
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
};

export default TopbarWidget;
