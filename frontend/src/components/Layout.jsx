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
    logo: '/assets/logo.png',
    favicon: '/assets/favicon.ico'
  });
  const [faviconLoaded, setFaviconLoaded] = useState(false);

  useEffect(() => {
    // Get branding from window object (set by server)
    if (window.PRESWALD_BRANDING) {
      console.log('Received branding:', window.PRESWALD_BRANDING);
      setBranding(window.PRESWALD_BRANDING);
      
      // Update document title
      document.title = window.PRESWALD_BRANDING.name;

      // Update favicon links
      const updateFaviconLinks = (faviconUrl) => {
        // Remove any existing favicon links
        const existingLinks = document.querySelectorAll("link[rel*='icon']");
        existingLinks.forEach(link => link.remove());

        // Create new favicon links
        const iconLink = document.createElement('link');
        iconLink.type = 'image/x-icon';
        iconLink.rel = 'icon';
        iconLink.href = faviconUrl;
        document.head.appendChild(iconLink);

        const shortcutLink = document.createElement('link');
        shortcutLink.type = 'image/x-icon';
        shortcutLink.rel = 'shortcut icon';
        shortcutLink.href = faviconUrl;
        document.head.appendChild(shortcutLink);
      };

      // Function to check if favicon is accessible
      const checkFavicon = () => {
        fetch(window.PRESWALD_BRANDING.favicon)
          .then(response => {
            if (response.ok) {
              setFaviconLoaded(true);
              console.log('Favicon loaded successfully');
              updateFaviconLinks(window.PRESWALD_BRANDING.favicon);
            } else {
              throw new Error('Favicon not found');
            }
          })
          .catch(error => {
            console.warn('Favicon failed to load, retrying in 1 second...', error);
            setTimeout(checkFavicon, 1000);
          });
      };

      checkFavicon();
      
    } else {
      console.warn('No PRESWALD_BRANDING found in window object');
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