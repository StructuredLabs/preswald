'use client';

import { Menu, PanelLeft, PanelLeftClose } from 'lucide-react';

import React from 'react';

import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

const TopbarWidget = ({ branding = window.PRESWALD_BRANDING, isCollapsed = false }) => {
  return (
    <div className="topbar">
      {/* Desktop collapse button */}
      <Button
        variant="ghost"
        size="icon"
        className="desktop-collapse-button"
        aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {isCollapsed ? (
          <PanelLeft className="icon-button" />
        ) : (
          <PanelLeftClose className="icon-button" />
        )}
      </Button>

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
