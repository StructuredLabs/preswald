'use client';

import { X } from 'lucide-react';

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';

import { cn } from '@/lib/utils';

export default function Sidebar({
  sidebarOpen,
  setSidebarOpen,
  navigation,
  branding,
  isCollapsed,
}) {
  const location = useLocation();
  const primaryColor = branding?.primaryColor || '#000000';

  const NavContent = ({ isMobile = false }) => (
    <div className="sidebar-container">
      <div className="sidebar-content">
        <div className="sidebar-nav">
          {!isMobile && (
            <div className="sidebar-header">
              <img
                className="sidebar-logo"
                src={`${branding?.logo}?timstamp=${new Date().getTime()}`}
                alt={branding?.name}
              />
              {!isCollapsed && <span className="sidebar-title">{branding?.name}</span>}
            </div>
          )}
          <nav className="sidebar-nav-list">
            <ul role="list" className="sidebar-nav-items">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        onClick={() => isMobile && setSidebarOpen(false)}
                        className={cn(
                          'sidebar-nav-link',
                          location.pathname === item.href
                            ? 'sidebar-nav-link-active'
                            : 'sidebar-nav-link-hover',
                          isCollapsed && !isMobile && 'justify-center px-2',
                          location.pathname === item.href
                            ? { color: primaryColor }
                            : 'text-muted-foreground hover:text-foreground'
                        )}
                        title={isCollapsed && !isMobile ? item.name : undefined}
                      >
                        <item.icon
                          className={cn(
                            'sidebar-icon',
                            isCollapsed && !isMobile && 'transform-gpu'
                          )}
                          style={{
                            color: location.pathname === item.href ? primaryColor : undefined,
                          }}
                          aria-hidden="true"
                        />
                        {(!isCollapsed || isMobile) && (
                          <span className="transition-opacity duration-200">{item.name}</span>
                        )}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
        <div className="sidebar-footer">
          Built By{' '}
          <a href="https://github.com/structuredlabs/preswald" className="sidebar-footer-link">
            Preswald
          </a>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="sidebar-mobile">
          <SheetHeader className="sidebar-mobile-header">
            <div className="flex items-center justify-between">
              <SheetTitle className="sidebar-mobile-title">
                <img
                  className="sidebar-logo"
                  src={`${branding?.logo}?timstamp=${new Date().getTime()}`}
                  alt={branding?.name}
                />
                <span>{branding?.name}</span>
              </SheetTitle>
            </div>
          </SheetHeader>
          <div className="sidebar-mobile-content">
            <NavContent isMobile={true} />
          </div>
        </SheetContent>
      </Sheet>

      {/* Desktop Sidebar */}
      <div
        className={cn(
          'sidebar-desktop',
          isCollapsed ? 'sidebar-desktop-collapsed' : 'sidebar-desktop-expanded'
        )}
      >
        <div className="sidebar-desktop-content">
          <NavContent />
        </div>
      </div>
    </>
  );
}
