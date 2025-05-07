import { HomeIcon } from '@heroicons/react/24/solid';
import { Menu } from 'lucide-react';

import React, { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Sidebar } from '@/components/ui/sidebar';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  // Add more navigation items here as needed
];

const SidebarWidget = ({ id, defaultOpen = false, ...props }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(!defaultOpen);
  const customBranding = props.branding || {};
  const branding = {
    logo: customBranding.logo || window.PRESWALD_BRANDING?.logo,
    name: customBranding.name || window.PRESWALD_BRANDING?.name,
    primaryColor: window.PRESWALD_BRANDING?.primaryColor,
  };

  return (
    <>
      <Button
        variant="outline"
        size="icon"
        className="fixed left-4 top-4 z-50 lg:hidden"
        onClick={() => setSidebarOpen(true)}
        aria-label="Open sidebar"
      >
        <Menu className="h-4 w-4" />
      </Button>

      <Sidebar
        id={id}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
        navigation={navigation}
        branding={branding}
      />
    </>
  );
};

export default SidebarWidget;
