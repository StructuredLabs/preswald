import { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { websocket } from "./utils/websocket";
import Layout from "./components/Layout";
import Dashboard from "./components/pages/Dashboard";
import Connections from "./components/pages/Connections";
import Metrics from "./components/pages/Metrics";
import Entities from "./components/pages/Entities";
import Schedules from "./components/pages/Schedules";
import Queries from "./components/pages/Queries";
import Definitions from "./components/pages/Definitions";

const App = () => {
  const [components, setComponents] = useState([]);
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

    document.addEventListener("visibilitychange", updateTitle);
    return () => document.removeEventListener("visibilitychange", updateTitle);
  }, [config]);

  const handleWebSocketMessage = (message) => {
    console.log("[App] Received WebSocket message:", message);

    switch (message.type) {
      case "components":
        refreshComponentsList(message.components);
        break;

      case "error":
        handleError(message.content);
        break;

      case "connection_status":
        updateConnectionStatus(message);
        break;

      case "config": // TODO: not used anywhere
        setConfig(message.config);
        break;

      // state_update and initial_state are handled by websocket.js
    }
  };

  const refreshComponentsList = (components) => {
    const updatedComponents = components.map((component) => {
      if (component.id) {
        const currentState = websocket.getComponentState(component.id);
        return {
          ...component,
          value: currentState !== undefined ? currentState : component.value,
          error: null,
        };
      }
      return component;
    });
    setComponents(updatedComponents);
    setError(null);
  };

  const handleError = (errorContent) => {
    console.error("[App] Received error:", errorContent);
    setError(errorContent.message);

    if (errorContent.componentId) {
      setComponents((prevComponents) =>
        prevComponents.map((component) =>
          component.id === errorContent.componentId
            ? { ...component, error: errorContent.message }
            : component
        )
      );
    }
  };

  const handleComponentUpdate = (componentId, value) => {
    try {
      websocket.updateComponentState(componentId, value);
    } catch (error) {
      console.error("[App] Error updating component state:", error);
      setComponents((prevComponents) =>
        prevComponents.map((component) =>
          component.id === componentId
            ? { ...component, error: error.message }
            : component
        )
      );
    }
  };

  const updateConnectionStatus = (message) => {
    setIsConnected(message.connected);
    setError(
      message.connected
        ? null
        : "Lost connection to server. Attempting to reconnect..."
    );
  };

  const renderLoadingState = () => (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Connecting to server...</p>
      </div>
    </div>
  );

  return (
    <Router>
      <Layout>
        {!isConnected ? (
          renderLoadingState
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
            <Route path="/metrics" element={<Metrics />} />
            <Route path="/entities" element={<Entities />} />
            <Route path="/schedules" element={<Schedules />} />
            <Route path="/definitions" element={<Definitions />} />
            <Route path="/queries" element={<Queries />} />
          </Routes>
        )}
      </Layout>
    </Router>
  );
};

export default App;
