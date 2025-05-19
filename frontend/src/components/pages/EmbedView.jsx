import React, { useEffect, useState, useRef } from 'react';
import DynamicComponents from '../DynamicComponents';

/**
 * EmbedView component for embedded app or single component view.
 * This provides a minimal layout without navigation, toolbars, etc.
 */
const EmbedView = () => {
  const [componentData, setComponentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const containerRef = useRef(null);
  
  // Auto-resize handler for iframes
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Create a ResizeObserver to detect size changes
    const resizeObserver = new ResizeObserver(() => {
      // Send message to parent window with new height
      if (window.parent !== window) {
        window.parent.postMessage({ 
          height: containerRef.current.scrollHeight,
          type: 'preswald-resize'
        }, '*');
      }
    });
    
    // Start observing
    resizeObserver.observe(containerRef.current);
    
    // Stop observing on cleanup
    return () => {
      resizeObserver.disconnect();
    };
  }, [componentData]);
  
  // Handle initial data load
  useEffect(() => {
    const handleComponentUpdate = (event) => {
      if (event.data && event.data.type === 'components') {
        setComponentData(event.data.components);
        setLoading(false);
      } else if (event.data && event.data.type === 'error') {
        setError(event.data.content);
        setLoading(false);
      }
    };
    
    // Add message event listener
    window.addEventListener('message', handleComponentUpdate);
    
    // Connect via WebSocket for embedded view
    const connectWebSocket = async () => {
      try {
        const embedConfig = window.EMBED_CONFIG || { embed_mode: true };
        const clientId = `embed-${Date.now()}`;
        
        // Connect to WebSocket with embed flag
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${clientId}`);
        
        ws.onopen = () => {
          // Send init message with embed mode
          ws.send(JSON.stringify({ 
            type: 'init',
            embed_mode: true,
            component_id: embedConfig.component_id 
          }));
        };
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          if (data.type === 'components') {
            if (embedConfig.component_id) {
              // Filter to just the requested component if specified
              const filteredComponents = filterComponentById(data.components, embedConfig.component_id);
              setComponentData(filteredComponents);
            } else {
              setComponentData(data.components);
            }
            setLoading(false);
          } else if (data.type === 'error') {
            setError(data.content);
            setLoading(false);
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError({ message: 'Failed to connect to the server' });
          setLoading(false);
        };
        
        ws.onclose = () => {
          console.log('WebSocket connection closed');
        };
        
        // Store the WebSocket connection for cleanup
        return ws;
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
        setError({ message: 'Failed to connect to the server' });
        setLoading(false);
      }
    };
    
    const wsConnection = connectWebSocket();
    
    // Cleanup function
    return () => {
      window.removeEventListener('message', handleComponentUpdate);
      if (wsConnection) {
        wsConnection.then(ws => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
          }
        });
      }
    };
  }, []);
  
  // Filter components to return only the specified component and its dependencies
  const filterComponentById = (components, componentId) => {
    if (!components || !componentId) return components;
    
    // Create a new components object with the same structure
    const filteredComponents = { ...components };
    
    // If components use a rows structure, filter them
    if (filteredComponents.rows) {
      const flattenedComponents = [];
      
      // Find the specified component in the rows
      filteredComponents.rows.forEach(row => {
        row.forEach(component => {
          if (component.id === componentId) {
            flattenedComponents.push(component);
          }
        });
      });
      
      // Create a single row with the filtered component
      filteredComponents.rows = flattenedComponents.length > 0 ? [flattenedComponents] : [];
    }
    
    return filteredComponents;
  };
  
  return (
    <div className="embed-container" ref={containerRef}>
      {loading && <div className="embed-loading">Loading...</div>}
      
      {error && (
        <div className="embed-error">
          <h3>Error</h3>
          <p>{error.message}</p>
        </div>
      )}
      
      {componentData && !loading && !error && (
        <DynamicComponents components={componentData} />
      )}
    </div>
  );
};

export default EmbedView; 