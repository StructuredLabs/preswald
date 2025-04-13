import { useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import { BrowserRouter as Router } from 'react-router-dom';

import Layout from './components/Layout';
import LoadingState from './components/LoadingState';
import Dashboard from './components/pages/Dashboard';
import { comm } from './utils/websocket';

const App = () => {
  const [components, setComponents] = useState({ rows: [] });
  const [error, setError] = useState(null);
  const [config, setConfig] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [areComponentsLoading, setAreComponentsLoading] = useState(true);

  useEffect(() => {
    comm.connect();

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

      case 'error':
        handleError(message.content);
        break;

      case 'connection_status':
        updateConnectionStatus(message);
        break;

      case 'config':
        setConfig(message.config);
        break;

      case 'initial_state':
        // Handle initial state
        console.log('[App] Received initial state:', message);
        break;
    }
  };

  const refreshComponentsList = (components) => {
    if (!components || !components.rows) {
      setAreComponentsLoading(false);
      console.warn('[App] Invalid components data received:', components);
      setComponents({ rows: [] });
      return;
    }

    try {
      const tabComponentRegistry = {
        ids: new Set(),
        content: new Set(),
      };

      components.rows.forEach((row) => {
        row.forEach((component) => {
          if (component?.type === 'tab' && component.tabs) {
            component.tabs.forEach((tab) => {
              (tab.components || []).forEach((tabComponent) => {
                if (tabComponent?.id) {
                  tabComponentRegistry.ids.add(tabComponent.id);
                }
                if (typeof tabComponent === 'string') {
                  tabComponentRegistry.content.add(tabComponent.trim());
                }
                const content =
                  tabComponent?.content?.trim() ||
                  tabComponent?.markdown?.trim() ||
                  (typeof tabComponent?.value === 'string' ? tabComponent.value.trim() : '');
                if (content) {
                  tabComponentRegistry.content.add(content);
                }
              });
            });
          }
        });
      });

      const updatedRows = components.rows.map((row) =>
        row
          .filter((component) => {
            if (!component) return false;
            if (component.type === 'tab') return true;

            const content =
              component.content?.trim() ||
              component.markdown?.trim() ||
              (typeof component.value === 'string' ? component.value.trim() : '');

            return !(
              (component.id && tabComponentRegistry.ids.has(component.id)) ||
              (content && tabComponentRegistry.content.has(content))
            );
          })
          .map((component) => ({
            ...component,
            value: component?.id
              ? (comm.getComponentState(component.id) ?? component.value)
              : component.value,
            error: null,
          }))
      );

      console.log('[App] Final filtered components:', { rows: updatedRows });
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

  const updateConnectionStatus = (message) => {
    setIsConnected(message.connected);
    setError(message.connected ? null : 'Lost connection. Attempting to reconnect...');
  };

  console.log('[App] Rendering with:', { components, isConnected, error });
  console.log(window.location.pathname);

  return (
    <Router>
      <Layout>
        {!isConnected || areComponentsLoading ? (
          <LoadingState isConnected={isConnected} />
        ) : (
          <Dashboard
            components={components}
            error={error}
            handleComponentUpdate={handleComponentUpdate}
          />
        )}
      </Layout>
    </Router>
  );
};

export default App;
