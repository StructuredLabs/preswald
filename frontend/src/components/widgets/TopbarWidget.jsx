'use client';

import React from 'react';

const TopbarWidget = ({ branding = window.PRESWALD_BRANDING, isCollapsed = false }) => {
  return (
    <div className="topbar">
      <div className="topbar-content">
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* Mobile branding */}
          <div className="branding-container">
            <img
              className="branding-logo"
              src={`${branding?.logo}?timstamp=${new Date().getTime()}`}
              alt={branding?.name}
            />
            <span className="branding-name">{branding?.name}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopbarWidget;
