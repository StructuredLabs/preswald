import { FolderIcon, HomeIcon } from '@heroicons/react/24/solid';
import { Menu } from 'lucide-react';
import PropTypes from 'prop-types';

import { useState } from 'react';
import { createPortal } from 'react-dom';

import { Button } from '@/components/ui/button';
import { Sidebar } from '@/components/ui/sidebar';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Data Files', href: '/data', icon: FolderIcon },
];

const SidebarWidget = ({ defaultOpen = false }) => {
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
      {document.getElementById('mobile-menu-button-portal') &&
        createPortal(<MobileMenuButton />, document.getElementById('mobile-menu-button-portal'))}

      {document.getElementById('sidebar-portal') &&
        createPortal(
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

SidebarWidget.propTypes = {
  defaultOpen: PropTypes.bool,
  // Include any additional props that might be passed via the ...props spread
  className: PropTypes.string,
  id: PropTypes.string,
  style: PropTypes.object,
};

SidebarWidget.defaultProps = {
  defaultOpen: false,
};

export default SidebarWidget;
