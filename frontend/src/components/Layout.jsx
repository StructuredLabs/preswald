'use client'

import { ChartBarIcon, ClockIcon, DocumentTextIcon, GlobeAltIcon, HomeIcon, MagnifyingGlassIcon, ServerIcon } from "@heroicons/react/24/solid";
import { useEffect, useState } from 'react'

import Content from "./Content";
import Sidebar from "./Sidebar";
import Topbar from "./TopBar";

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon, current: true },
  { name: 'Queries', href: '/queries', icon: MagnifyingGlassIcon, current: false },
  { name: 'Metrics', href: '/metrics', icon: ChartBarIcon, current: false },
  { name: 'Schedules', href: '/schedules', icon: ClockIcon, current: false },  
  { name: 'Connections', href: '/connections', icon: ServerIcon, current: false },
  { name: 'Entities', href: '/entities', icon: GlobeAltIcon, current: false },
  { name: 'Definitions', href: '/definitions', icon: DocumentTextIcon, current: false },
];

export default function Example({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [branding, setBranding] = useState({
    name: 'Preswald',
    logo: '/assets/default-logo.png',
    favicon: '/assets/favicon.ico'
  });

  useEffect(() => {
    // Get branding from window object (set by server)
    if (window.PRESWALD_BRANDING) {
      setBranding(window.PRESWALD_BRANDING);
      // Update document title
      document.title = window.PRESWALD_BRANDING.name;
    }
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <>
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        navigation={navigation}
        branding={branding}
        isCollapsed={sidebarCollapsed}
      />
      <div className={`transition-all duration-300 ${sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-80'}`}>
        <Topbar 
          setSidebarOpen={setSidebarOpen} 
          branding={branding} 
          onToggleSidebar={toggleSidebar}
          isCollapsed={sidebarCollapsed}
        />
        <main>
          <Content>{children}</Content>
        </main>
      </div>
    </>
  );
}