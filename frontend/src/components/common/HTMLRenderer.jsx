import React, { useEffect, useRef } from 'react';

const HTMLRenderer = ({ html, className }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!html) return;
    const container = containerRef.current;
    if (!container) return;

    // Clear any existing content.
    container.innerHTML = '';

    // Create a temporary element to parse the HTML.
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    // Extract external and inline script elements.
    const externalScripts = Array.from(tempDiv.querySelectorAll('script[src]'));
    const inlineScripts = Array.from(tempDiv.querySelectorAll('script:not([src])'));

    // Remove all script tags from tempDiv.
    externalScripts.forEach((script) => script.remove());
    inlineScripts.forEach((script) => script.remove());

    // Append non-script nodes to the container.
    while (tempDiv.firstChild) {
      container.appendChild(tempDiv.firstChild);
    }

    // Helper to load an external script.
    const loadScript = (script) => {
      return new Promise((resolve, reject) => {
        const newScript = document.createElement('script');
        // Copy all attributes.
        Array.from(script.attributes).forEach((attr) => {
          newScript.setAttribute(attr.name, attr.value);
        });
        newScript.async = false; // preserve execution order
        newScript.onload = resolve;
        newScript.onerror = () => reject(new Error(`Failed to load script: ${script.src}`));
        document.head.appendChild(newScript);
      });
    };

    // Load external scripts sequentially.
    const loadExternalScripts = async () => {
      for (const script of externalScripts) {
        await loadScript(script);
      }
    };

    loadExternalScripts()
      .then(() => {
        // Once external scripts are loaded, wait a brief moment then append inline scripts.
        setTimeout(() => {
          inlineScripts.forEach((script) => {
            const newScript = document.createElement('script');
            newScript.text = script.textContent;
            container.appendChild(newScript);
          });
        }, 50); // delay can be adjusted if needed
      })
      .catch((err) => {
        console.error('Error loading external scripts:', err);
      });
  }, [html]);

  return <div ref={containerRef} className={className} />;
};

export default HTMLRenderer;
