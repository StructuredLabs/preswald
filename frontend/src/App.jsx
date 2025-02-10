import { useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import { BrowserRouter as Router } from 'react-router-dom';

import Layout from './components/Layout';
import Connections from './components/pages/Connections';
import Dashboard from './components/pages/Dashboard';
import Definitions from './components/pages/Definitions';
import { websocket } from './utils/websocket';

const App = () => {
  const [components, setComponents] = useState({ rows: [] });
  const [error, setError] = useState(null);
  const [config, setConfig] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    websocket.connect();

    const unsubscribe = websocket.subscribe(handleWebSocketMessage);

    return () => {
      unsubscribe();
      websocket.disconnect();
    };
  }, []);

  // TODO: where is this used, if at all?
  useEffect(() => {
    // Update document title based on config
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

  const handleWebSocketMessage = (message) => {
    console.log('[App] Received WebSocket message:', message);

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
      console.warn('[App] Invalid components data received:', components);
      setComponents({ rows: [] });
      return;
    }

    try {
      const updatedRows = components.rows.map((row) =>
        row.map((component) => {
          if (!component || !component.id) return component;

          const currentState = websocket.getComponentState(component.id);
          return {
            ...component,
            value: currentState !== undefined ? currentState : component.value,
            error: null,
          };
        })
      );

      console.log('[App] Updating components with:', { rows: updatedRows });
      setComponents({ rows: updatedRows });
      setError(null);
    } catch (error) {
      console.error('[App] Error processing components:', error);
      setError('Error processing components data');
      setComponents({ rows: [] });
    }
  };

  const handleError = (errorContent) => {
    console.error('[App] Received error:', errorContent);
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
      websocket.updateComponentState(componentId, value);
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
    setError(message.connected ? null : 'Lost connection to server. Attempting to reconnect...');
  };

  const LoadingState = () => (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Connecting to server...</p>
      </div>
    </div>
  );

  console.log('[App] Rendering with:', { components, isConnected, error });

  return (
    <Router>
      <Layout>
        {!isConnected ? (
          <LoadingState />
        ) : (
          <Routes>
            <Route
              path="/"
              element={
                <Dashboard
                  components={components}
                  error={error}
                  handleComponentUpdate={handleComponentUpdate}
                />
              }
            />
            <Route path="/connections" element={<Connections />} />
            <Route path="/definitions" element={<Definitions />} />
          </Routes>
        )}
      </Layout>
    </Router>
    // <Layout>
    //    {!isConnected ? (
    //       <LoadingState />
    //     ) : (
    //       <Dashboard
    //         components={components}
    //         error={error}
    //         handleComponentUpdate={handleComponentUpdate}
    //       />
    //     )}
    // </Layout>
  );
};

export default App;
