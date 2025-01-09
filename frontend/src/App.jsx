import { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { websocket } from "./utils/websocket";
import { componentStore } from "./utils/componentStore";
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
    const unsubscribeStore = componentStore.subscribe((components) => {
      setComponents(components);
      setError(null); // Clear errors when component list refreshes
    });

    const unsubscribeWebSocket = websocket.subscribe(handleWebSocketMessage);

    websocket.connect();

    return () => {
      unsubscribeStore();
      unsubscribeWebSocket();
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
      case "error":
        console.error("[App] Received error:", message.content);
        if (!message.content.componentId) {
          // Only handle non-component errors
          setError(message.content.message);
        }
        break;

      case "connection_status":
        setIsConnected(message.connected);
        setError(
          message.connected
            ? null
            : "Lost connection to server. Attempting to reconnect..."
        );
        break;

      case "config": // TODO: not used anywhere
        setConfig(message.config);
        break;

      // components, state_update and initial_state are handled by websocket.js
    }
  };

  const handleComponentUpdate = (componentId, value) => {
    try {
      websocket.updateComponentState(componentId, value);
    } catch (error) {
      console.error("[App] Error updating component state:", error);
    }
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
