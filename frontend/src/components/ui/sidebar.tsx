"use client";

import { X } from "lucide-react";
import React, { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, PanelLeft, PanelLeftClose } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

const Sidebar = ({
  sidebarOpen,
  setSidebarOpen,
  navigation,
  branding,
  isCollapsed,
  setIsCollapsed,
}) => {
  const location = useLocation();
  const primaryColor = branding?.primaryColor || "#000000";

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
              {!isCollapsed && (
                <span className="sidebar-title">{branding?.name}</span>
              )}
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
                          "sidebar-nav-link",
                          location.pathname === item.href
                            ? "sidebar-nav-link-active"
                            : "sidebar-nav-link-hover",
                          isCollapsed && !isMobile && "justify-center px-2",
                          location.pathname === item.href
                            ? { color: primaryColor }
                            : "text-muted-foreground hover:text-foreground",
                        )}
                        title={isCollapsed && !isMobile ? item.name : undefined}
                      >
                        <item.icon
                          className={cn(
                            "sidebar-icon",
                            isCollapsed && !isMobile && "transform-gpu",
                          )}
                          style={{
                            color:
                              location.pathname === item.href
                                ? primaryColor
                                : undefined,
                          }}
                          aria-hidden="true"
                        />
                        {(!isCollapsed || isMobile) && (
                          <span className="transition-opacity duration-200">
                            {item.name}
                          </span>
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
          Built By{" "}
          <a
            href="https://github.com/structuredlabs/preswald"
            className="sidebar-footer-link"
          >
            Preswald
          </a>
        </div>
      </div>
    </div>
  );

  const applyMainLayoutPadding = (collapsed) => {
    const mainLayout = document.querySelector(".main-content-layout");
    if (!mainLayout) {
      return;
    }

    if (collapsed) {
      mainLayout.classList.add("main-content-collapsed-sidebar");
      mainLayout.classList.remove("main-content-open-sidebar");
    } else {
      mainLayout.classList.remove("main-content-collapsed-sidebar");
      mainLayout.classList.add("main-content-open-sidebar");
    }
  };

  useEffect(() => {
    applyMainLayoutPadding(isCollapsed);
  }, [isCollapsed]);

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
          "sidebar-desktop",
          isCollapsed
            ? "sidebar-desktop-collapsed"
            : "sidebar-desktop-expanded",
        )}
      >
        <Button
          variant="ghost"
          size="icon"
          className="desktop-collapse-button"
          onClick={() => setIsCollapsed((prev) => !prev)}
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? (
            <PanelLeft className="icon-button" />
          ) : (
            <PanelLeftClose className="icon-button" />
          )}
        </Button>

        <div className="sidebar-desktop-content">
          <NavContent />
        </div>
      </div>
    </>
  );
};

export { Sidebar };
