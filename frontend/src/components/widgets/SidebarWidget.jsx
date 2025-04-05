import { HomeIcon } from '@heroicons/react/24/solid';
import { Menu } from 'lucide-react';

import React, { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Sidebar } from '@/components/ui/sidebar';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  // Add more navigation items here as needed
];

const SidebarWidget = ({ defaultOpen = false, ...props }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(!defaultOpen);

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
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
        navigation={navigation}
        branding={window.PRESWALD_BRANDING}
      />
    </>
  );
};

export default SidebarWidget;
