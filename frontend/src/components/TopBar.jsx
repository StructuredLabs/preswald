'use client';

import { Menu, PanelLeft, PanelLeftClose } from 'lucide-react';

import { Button } from '@/components/ui/button';
import React from 'react';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

export default function Topbar({ setSidebarOpen, branding, onToggleSidebar, isCollapsed }) {
  return (
    <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b bg-background px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={() => setSidebarOpen(true)}
        aria-label="Open sidebar"
      >
        <Menu className="h-6 w-6" />
      </Button>

      {/* Desktop collapse button */}
      <Button
        variant="ghost"
        size="icon"
        className="hidden lg:flex"
        onClick={onToggleSidebar}
        aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {isCollapsed ? (
          <PanelLeft className="h-6 w-6 transition-transform duration-200" />
        ) : (
          <PanelLeftClose className="h-6 w-6 transition-transform duration-200" />
        )}
      </Button>

      {/* Separator */}
      <Separator orientation="vertical" className="h-6 lg:hidden" />

      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* Mobile branding */}
          <div className="flex lg:hidden items-center">
            <img className="h-8 w-8" src={`${branding?.logo}?timstamp=${new Date().getTime()}`} alt={branding?.name} />
            <span className="ml-3 text-lg font-semibold">{branding?.name}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
