import { HomeIcon } from '@heroicons/react/24/solid';
import { Menu } from 'lucide-react';

import React, { useState } from 'react';
import { createPortal } from 'react-dom';

import { Button } from '@/components/ui/button';
import { Sidebar } from '@/components/ui/sidebar';

const navigation = [{ name: 'Dashboard', href: '/', icon: HomeIcon }];

const SidebarWidget = ({ defaultOpen = false, ...props }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(!defaultOpen);

  const MobileMenuButton = () => {
    return (
      <Button
        variant="ghost"
        size="icon"
        className="mobile-menu-button"
        onClick={() => setSidebarOpen(true)}
        aria-label="Open sidebar"
      >
        <Menu className="icon-button" />
      </Button>
    );
  };

  return (
    <>
      {createPortal(<MobileMenuButton />, document.getElementById('mobile-menu-button-portal'))}

      {createPortal(
        <Sidebar
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          isCollapsed={isCollapsed}
          setIsCollapsed={setIsCollapsed}
          navigation={navigation}
          branding={window.PRESWALD_BRANDING}
        />,
        document.getElementById('sidebar-portal')
      )}
    </>
  );
};

export default SidebarWidget;
