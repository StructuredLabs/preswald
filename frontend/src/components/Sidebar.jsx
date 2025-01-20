'use client';

import { Link, useLocation } from 'react-router-dom';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

import { Button } from "@/components/ui/button";
import React from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Sidebar({ sidebarOpen, setSidebarOpen, navigation, branding, isCollapsed }) {
  const location = useLocation();
  const primaryColor = branding?.primaryColor || '#000000';

  const NavContent = ({ isMobile = false }) => (
    <ScrollArea className="flex grow flex-col gap-y-5 overflow-y-auto">
      {!isMobile && (
        <div className="flex h-16 shrink-0 items-center">
          <img
            className="h-8 w-8"
            src={branding?.logo}
            alt={branding?.name}
          />
          {!isCollapsed && (
            <span className="ml-4 text-lg font-semibold transition-opacity duration-200">{branding?.name}</span>
          )}
        </div>
      )}
      <nav className="flex flex-1 flex-col">
        <ul role="list" className="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" className="-mx-2 space-y-1">
              {navigation.map((item) => (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    onClick={() => isMobile && setSidebarOpen(false)}
                    className={cn(
                      "flex items-center gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 transition-all duration-200",
                      location.pathname === item.href
                        ? "bg-accent"
                        : "hover:bg-accent",
                      isCollapsed && !isMobile && "justify-center px-2",
                      location.pathname === item.href
                        ? { color: primaryColor }
                        : "text-muted-foreground hover:text-foreground"
                    )}
                    title={isCollapsed && !isMobile ? item.name : undefined}
                  >
                    <item.icon
                      className={cn(
                        "h-6 w-6 shrink-0 transition-transform duration-200",
                        isCollapsed && !isMobile && "transform-gpu"
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
    </ScrollArea>
  );

  return (
    <>
      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent 
          side="left" 
          className={cn(
            "fixed inset-y-0 left-0",
            "flex w-[280px] flex-col",
            "border-r bg-background p-0",
            "data-[state=closed]:duration-300 data-[state=open]:duration-500",
            "data-[state=closed]:animate-slide-to-left data-[state=open]:animate-slide-from-left",
            "[&>button]:top-4 [&>button]:right-4 [&>button]:h-8 [&>button]:w-8"
          )}
        >
          <SheetHeader className="p-4 border-b">
            <div className="flex items-center justify-between">
              <SheetTitle className="flex items-center gap-2">
                <img
                  className="h-8 w-8"
                  src={branding?.logo}
                  alt={branding?.name}
                />
                <span>{branding?.name}</span>
              </SheetTitle>
            </div>
          </SheetHeader>
          <div className="flex-1 overflow-hidden px-4 py-2">
            <NavContent isMobile={true} />
          </div>
        </SheetContent>
      </Sheet>

      {/* Desktop Sidebar */}
      <div className={cn(
        'hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:flex-col',
        isCollapsed ? 'lg:w-20' : 'lg:w-80',
        'border-r bg-background transition-all duration-300 ease-in-out transform-gpu'
      )}>
        <div className="flex-1 overflow-hidden px-4 py-2">
          <NavContent />
        </div>
      </div>
    </>
  );
}