import { Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';

import Dashboard from './components/pages/Dashboard';
import Layout from './components/Layout';
import LoadingState from './components/LoadingState';
import { BrowserRouter as Router } from 'react-router-dom';
import { comm } from './utils/websocket';

const App = () => {
  const [components, setComponents] = useState({ rows: [] });
  const [error, setError] = useState(null);
  const [transformErrors, setTransformErrors] = useState([]);
  const [config, setConfig] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [areComponentsLoading, setAreComponentsLoading] = useState(true);

  useEffect(() => {
    comm.connect();
    console.log('[App] Connected to comm');
    const unsubscribe = comm.subscribe(handleMessage);

    return () => {
      unsubscribe();
      comm.disconnect();
    };
  }, []);

  useEffect(() => {
    const updateTitle = () => {
      const title = config?.project?.title;
      if (title) {
        document.title = title;
      }
    };

    updateTitle();
    document.addEventListener('visibilitychange', updateTitle);
    return () => document.removeEventListener('visibilitychange', updateTitle);
  }, [config]);

  const handleMessage = (message) => {
    console.log('[App] Received message:', message);

    switch (message.type) {
      case 'components':
        if (message.components) {
          refreshComponentsList(message.components);
        }
        break;

      case 'bulk_update':
        // Handle bulk state updates efficiently
        if (message.states) {
          handleBulkStateUpdate(message.states);
        }
        break;

      case 'error':
        handleError(message.content);
        break;

      case 'errors:result':
        handleTransformErrors(message.errors, message.components);
        break;

      case 'connection_status':
        updateConnectionStatus(message);
        break;

      case 'config':
        setConfig(message.config);
        break;

      case 'initial_state':
        // Handle initial state with bulk processing
        console.log('[App] Received initial state:', message);
        if (message.states) {
          handleBulkStateUpdate(message.states);
        }
        break;
    }
  };

  const handleBulkStateUpdate = (stateUpdates) => {
    const startTime = performance.now();
    
    try {
      if (!stateUpdates || typeof stateUpdates !== 'object') {
        console.warn('[App] Invalid bulk state updates received:', stateUpdates);
        return;
      }

      const updateCount = Object.keys(stateUpdates).length;
      console.log(`[App] Processing bulk state update: ${updateCount} components`);

      // Apply bulk state updates to current components
      setComponents((prevState) => {
        if (!prevState || !prevState.rows) return { rows: [] };

        const updatedRows = prevState.rows.map((row) =>
          row.map((component) => {
            if (!component || !component.id) return component;

            // Check if this component has a state update
            if (stateUpdates.hasOwnProperty(component.id)) {
              return {
                ...component,
                value: stateUpdates[component.id],
                error: null, // Clear any previous errors
              };
            }

            return component;
          })
        );

        const processingTime = performance.now() - startTime;
        console.log(`[App] Bulk state update applied: ${updateCount} components in ${processingTime.toFixed(2)}ms`);

        return { rows: updatedRows };
      });

    } catch (error) {
      console.error('[App] Error processing bulk state update:', error);
      setError('Error processing bulk state update');
    }
  };

  const refreshComponentsList = async (components) => {
    if (!components || !components.rows) {
      setAreComponentsLoading(false);
      console.warn('[App] Invalid components data received:', components);
      setComponents({ rows: [] });
      return;
    }

    try {
      const startTime = performance.now();
      
      // Enhanced bulk processing approach - collect all component IDs first
      const componentIds = [];
      const componentMap = new Map(); // For faster lookups during processing
      
      components.rows.forEach((row, rowIndex) => {
        row.forEach((component, componentIndex) => {
          if (component && component.id) {
            componentIds.push(component.id);
            componentMap.set(component.id, { rowIndex, componentIndex, component });
          }
        });
      });

      // Bulk retrieve all component states with batching for large datasets
      const stateMap = new Map();
      const batchSize = 100; // Process in batches to avoid blocking UI thread
      
      for (let i = 0; i < componentIds.length; i += batchSize) {
        const batch = componentIds.slice(i, i + batchSize);
        batch.forEach((componentId) => {
          const currentState = comm.getComponentState(componentId);
          if (currentState !== undefined) {
            stateMap.set(componentId, currentState);
          }
        });
        
        // Allow UI updates between batches for very large component sets
        if (componentIds.length > 500 && i % 200 === 0) {
          // Use setTimeout to yield control back to the browser
          await new Promise(resolve => setTimeout(resolve, 0));
        }
      }

      // Process components with bulk-retrieved states using optimized approach
      const updatedRows = components.rows.map((row) =>
        row.map((component) => {
          if (!component || !component.id) return component;

          const currentState = stateMap.get(component.id);
          return {
            ...component,
            value: currentState !== undefined ? currentState : component.value,
            error: null,
          };
        })
      );

      const processingTime = performance.now() - startTime;
      
      // Enhanced performance metrics for production monitoring
      const metrics = {
        componentCount: componentIds.length,
        processingTime: processingTime.toFixed(2),
        stateHitRate: componentIds.length > 0 ? (stateMap.size / componentIds.length * 100).toFixed(1) : '0',
        batchCount: Math.ceil(componentIds.length / batchSize),
        timestamp: new Date().toISOString()
      };
      
      console.log(`[App] Enhanced bulk component processing completed: ${componentIds.length} components in ${processingTime.toFixed(2)}ms`);
      console.log('[App] Processing metrics:', metrics);
      
      setAreComponentsLoading(false);
      setComponents({ rows: updatedRows });
      setError(null);
    } catch (error) {
      console.error('[App] Error processing components:', error);
      setAreComponentsLoading(false);
      setError('Error processing components data');
      setComponents({ rows: [] });
    }
  };

  const handleError = (errorContent) => {
    console.error('[App] Received error:', errorContent);
    setAreComponentsLoading(false);
    setError(errorContent.message);

    if (errorContent.componentId) {
      setComponents((prevState) => {
        if (!prevState || !prevState.rows) return { rows: [] };

        return {
          rows: prevState.rows.map((row) =>
            row.map((component) =>
              component.id === errorContent.componentId
                ? { ...component, error: errorContent.message }
                : component
            )
          ),
        };
      });
    }
  };

  const handleTransformErrors = (errorContents, components = null) => {
    console.error('[App] Received transform errors:', {errorContents, components});
    setAreComponentsLoading(false);
    setTransformErrors(errorContents || []);
    if (components) {
      refreshComponentsList(components);
    }
  };

  const handleComponentUpdate = (componentId, value) => {
    try {
      comm.updateComponentState(componentId, value);
    } catch (error) {
      console.error('[App] Error updating component state:', error);
      setComponents((prevState) => {
        if (!prevState || !prevState.rows) return { rows: [] };

        return {
          rows: prevState.rows.map((row) =>
            row.map((component) =>
              component.id === componentId ? { ...component, error: error.message } : component
            )
          ),
        };
      });
    }
  };

  const handleBulkComponentUpdate = async (updates) => {
    const startTime = performance.now();
    
    try {
      if (!updates || typeof updates !== 'object') {
        console.warn('[App] Invalid bulk component updates:', updates);
        return;
      }

      const updateCount = Object.keys(updates).length;
      console.log(`[App] Processing bulk component update: ${updateCount} components`);

      // Use the communication layer's bulk update capability
      const result = await comm.bulkStateUpdate(updates);
      
      const processingTime = performance.now() - startTime;
      console.log(`[App] Bulk component update completed in ${processingTime.toFixed(2)}ms:`, {
        totalProcessed: result.totalProcessed,
        successCount: result.successCount,
        localChanges: result.localChanges,
        networkUpdates: result.networkUpdates
      });

      // Update UI state to reflect the changes
      setComponents((prevState) => {
        if (!prevState || !prevState.rows) return { rows: [] };

        const updatedRows = prevState.rows.map((row) =>
          row.map((component) => {
            if (!component || !component.id) return component;

            // Check if this component was updated
            if (updates.hasOwnProperty(component.id)) {
              return {
                ...component,
                value: updates[component.id],
                error: null, // Clear any previous errors
              };
            }

            return component;
          })
        );

        return { rows: updatedRows };
      });

    } catch (error) {
      console.error('[App] Error processing bulk component update:', error);
      setError('Error processing bulk component update');
    }
  };

  const updateConnectionStatus = (message) => {
    console.log('[App] Updating connection status:', message);
    setIsConnected(message.connected);
    setError(message.connected ? null : 'Lost connection. Attempting to reconnect...');
  };

  return (
    <Router>
      <Layout>
        {!isConnected || areComponentsLoading ? (
          <LoadingState isConnected={isConnected} />
        ) : (
          <Dashboard
            components={components}
            error={error}
            transformErrors={transformErrors}
            handleComponentUpdate={handleComponentUpdate}
          />
        )}
      </Layout>
    </Router>
  );
};

export default App;
