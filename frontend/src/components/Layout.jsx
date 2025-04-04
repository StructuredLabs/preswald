'use client';

import React, { useState } from 'react';
import { useEffect } from 'react';

import { PreswaldBadge } from './PreswaldBadge';

export default function Layout({ branding, children }) {
  const [faviconLoaded, setFaviconLoaded] = useState(false);

  useEffect(() => {
    // Get branding from window object (set by server)
    if (window.PRESWALD_BRANDING) {
      console.log('Received branding:', window.PRESWALD_BRANDING);

      // Update document title
      document.title = window.PRESWALD_BRANDING.name;

      // Update favicon links
      const updateFaviconLinks = (faviconUrl) => {
        // Remove any existing favicon links
        const existingLinks = document.querySelectorAll("link[rel*='icon']");
        existingLinks.forEach((link) => link.remove());

        // Create new favicon links
        const iconLink = document.createElement('link');
        iconLink.type = 'image/x-icon';
        iconLink.rel = 'icon';
        iconLink.href = `${faviconUrl}?timestamp=${new Date().getTime()}`;
        document.head.appendChild(iconLink);

        const shortcutLink = document.createElement('link');
        shortcutLink.type = 'image/x-icon';
        shortcutLink.rel = 'shortcut icon';
        shortcutLink.href = `${faviconUrl}?timestamp=${new Date().getTime()}`;
        document.head.appendChild(shortcutLink);
      };

      // Function to check if favicon is accessible
      const checkFavicon = () => {
        fetch(window.PRESWALD_BRANDING.favicon)
          .then((response) => {
            if (response.ok) {
              setFaviconLoaded(true);
              console.log('Favicon loaded successfully');
              updateFaviconLinks(window.PRESWALD_BRANDING.favicon);
            } else {
              throw new Error('Favicon not found');
            }
          })
          .catch((error) => {
            console.warn('Favicon failed to load, retrying in 1 second...', error);
            setTimeout(checkFavicon, 1000);
          });
      };

      checkFavicon();
    } else {
      console.warn('No PRESWALD_BRANDING found in window object');
    }
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <PreswaldBadge />
      <div className="flex min-h-screen relative">
        <main className="flex-1 main-content-layout relative">
          <div className="pt-14 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">{children}</div>
        </main>
      </div>
    </div>
  );
}
