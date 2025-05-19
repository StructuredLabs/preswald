import { decode } from '@msgpack/msgpack';

import { createWorker } from '../backend/service';

class WebSocketClient {
  constructor() {
    this.socket = null;
    this.callbacks = new Set();
    this.clientId = Math.random().toString(36).substring(7);
    this.isConnecting = false;
    this.componentStates = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.connections = [];
    this.pendingUpdates = {}; // Only store latest value for each component
  }

  connect() {
    if (this.isConnecting || (this.socket && this.socket.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] Already connected or connecting');
      return;
    }

    this.isConnecting = true;
    console.log('[WebSocket] Connecting...');

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log('[WebSocket] Connected successfully');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;

        Object.entries(this.pendingUpdates).forEach(([componentId, value]) => {
          this._sendComponentUpdate(componentId, value);
        });
        this.pendingUpdates = {};

        this._notifySubscribers({ type: 'connection_status', connected: true });
      };

      this.socket.onclose = (event) => {
        console.log('[WebSocket] Connection closed:', event);
        this.isConnecting = false;
        this.socket = null;
        this._notifySubscribers({ type: 'connection_status', connected: false });
        this._handleReconnect();
      };

      this.socket.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        this.isConnecting = false;
        this._notifySubscribers({
          type: 'error',
          content: { message: 'WebSocket connection error' },
        });
      };

      this.socket.onmessage = async (event) => {
        try {
          if (typeof event.data === 'string') {
            // Normal text message — parse as JSON
            const data = JSON.parse(event.data);
            console.log('[WebSocket] JSON Message received:', {
              ...data,
              timestamp: new Date().toISOString(),
            });

            switch (data.type) {
              case 'initial_state':
                this.componentStates = { ...data.states };
                console.log('[WebSocket] Initial states loaded:', this.componentStates);
                break;

              case 'state_update':
                if (data.component_id) {
                  this.componentStates[data.component_id] = data.value;
                }
                console.log('[WebSocket] Component state updated:', {
                  componentId: data.component_id,
                  value: data.value,
                });
                break;

              case 'components':
                if (data.components?.rows) {
                  data.components.rows.forEach((row) => {
                    row.forEach((component) => {
                      if (component.id && 'value' in component) {
                        this.componentStates[component.id] = component.value;
                        console.log('[WebSocket] Component state updated:', {
                          componentId: component.id,
                          value: component.value,
                        });
                      }
                    });
                  });
                }
                break;

              case 'connections_update':
                this.connections = data.connections || [];
                console.log('[WebSocket] Connections updated:', this.connections);
                break;
            }

            this._notifySubscribers(data);
          } else if (event.data instanceof Blob) {
            const buffer = await event.data.arrayBuffer();
            const decoded = decode(new Uint8Array(buffer));

            if (decoded?.type === 'image_update' && decoded.format === 'png') {
              const { component_id, data: binaryData, label } = decoded;

              // Convert image data (Uint8Array) to base64
              const base64 = `data:image/png;base64,${btoa(
                new Uint8Array(binaryData).reduce(
                  (data, byte) => data + String.fromCharCode(byte),
                  ''
                )
              )}`;

              // Update state and notify
              this.componentStates[component_id] = base64;
              this._notifySubscribers({
                type: 'image_update',
                component_id,
                value: base64,
                label,
              });
            } else {
              console.warn('[WebSocket] Unknown binary message format:', decoded);
            }
          } else {
            console.warn('[WebSocket] Unrecognized message format:', event.data);
          }
        } catch (error) {
          console.error('[WebSocket] Error processing message:', error);
          this._notifySubscribers({
            type: 'error',
            content: { message: 'Error processing server message' },
          });
        }
      };
    } catch (error) {
      console.error('[WebSocket] Error creating connection:', error);
      this.isConnecting = false;
      this._notifySubscribers({
        type: 'error',
        content: { message: 'Failed to create WebSocket connection' },
      });
    }
  }

  disconnect() {
    if (this.socket) {
      console.log('[WebSocket] Disconnecting...');
      this.socket.close();
      this.socket = null;
    }
  }

  _handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WebSocket] Max reconnection attempts reached');
      this._notifySubscribers({
        type: 'error',
        content: { message: 'Failed to reconnect after multiple attempts' },
      });
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);
    console.log(
      `[WebSocket] Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`
    );

    setTimeout(() => {
      if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
        console.log('[WebSocket] Attempting reconnection...');
        this.connect();
      }
    }, delay);
  }

  subscribe(callback) {
    this.callbacks.add(callback);
    return () => this.callbacks.delete(callback);
  }

  _notifySubscribers(message) {
    this.callbacks.forEach((callback) => {
      try {
        callback(message);
      } catch (error) {
        console.error('[WebSocket] Error in subscriber callback:', error);
      }
    });
  }

  getComponentState(componentId) {
    return this.componentStates[componentId];
  }

  updateComponentState(componentId, value) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      this.pendingUpdates.set(componentId, value);
      throw new Error('WebSocket connection not open');
    }
    return this._sendComponentUpdate(componentId, value);
  }

  _sendComponentUpdate(componentId, value) {
    const message = { type: 'component_update', states: { [componentId]: value } };
    try {
      this.socket.send(JSON.stringify(message));
      this.componentStates[componentId] = value;
      console.log('[WebSocket] Sent component update:', message);
    } catch (error) {
      console.error('[WebSocket] Error sending component update:', error);
      throw error;
    }
  }

  getConnections() {
    return this.connections;
  }
}

class PostMessageClient {
  constructor() {
    this.callbacks = new Set();
    this.componentStates = {};
    this.isConnected = false;
    this.pendingUpdates = {};
  }

  connect() {
    console.log('[PostMessage] Setting up listener...');
    window.addEventListener('message', this._handleMessage.bind(this)); // This is the real core of the postmessage client

    // Assume connected in browser context
    this.isConnected = true;
    this._notifySubscribers({ type: 'connection_status', connected: true });
    console.log('[PostMessage] Connected successfully');

    // Send pending updates
    Object.entries(this.pendingUpdates).forEach(([componentId, value]) => {
      this._sendComponentUpdate(componentId, value);
    });
    this.pendingUpdates = {};
  }

  disconnect() {
    console.log('[PostMessage] Disconnecting...');
    window.removeEventListener('message', this._handleMessage.bind(this));
    this.isConnected = false;
    this._notifySubscribers({ type: 'connection_status', connected: false });
  }

  _handleMessage(event) {
    if (!event.data) return;

    let data;
    try {
      // Handle both string and object messages
      data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
    } catch (error) {
      console.error('[PostMessage] Error parsing message:', error);
      return;
    }
    console.log('[PostMessage] Message received:', {
      ...data,
      timestamp: new Date().toISOString(),
    });
    switch (data.type) {
      case 'connection_status':
        this.isConnected = data.connected;
        console.log('[PostMessage] Connection status:', this.isConnected);
        this._notifySubscribers(data);
        break;

      case 'initial_state':
        this.componentStates = { ...data.states };
        console.log('[PostMessage] Initial states loaded:', this.componentStates);
        this._notifySubscribers(data);
        break;

      case 'state_update':
        if (data.component_id) {
          this.componentStates[data.component_id] = data.value;
        }
        console.log('[PostMessage] Component state updated:', {
          componentId: data.component_id,
          value: data.value,
        });
        this._notifySubscribers(data);
        break;

      case 'components':
        if (data.components && data.components.rows) {
          data.components.rows.forEach((row) => {
            row.forEach((component) => {
              if (component.id && 'value' in component) {
                this.componentStates[component.id] = component.value;
                console.log('[PostMessage] Component state updated:', {
                  componentId: component.id,
                  value: component.value,
                });
              }
            });
          });
        }
        this._notifySubscribers(data);
        break;

      case 'error':
        this._notifySubscribers(event.data);
        break;
    }
  }

  subscribe(callback) {
    this.callbacks.add(callback);
    return () => this.callbacks.delete(callback);
  }

  _notifySubscribers(message) {
    this.callbacks.forEach((callback) => {
      try {
        callback(message);
      } catch (error) {
        console.error('[PostMessage] Error in subscriber callback:', error);
      }
    });
  }

  getComponentState(componentId) {
    return this.componentStates[componentId];
  }

  updateComponentState(componentId, value) {
    if (!this.isConnected) {
      this.pendingUpdates.set(componentId, value);
      throw new Error('PostMessage connection not ready');
    }
    return this._sendComponentUpdate(componentId, value);
  }

  _sendComponentUpdate(componentId, value) {
    if (window.parent) {
      window.parent.postMessage(
        {
          type: 'component_update',
          id: componentId,
          value,
        },
        '*'
      );
      this.componentStates[componentId] = value;
      console.log('[PostMessage] Sent component update:', { id: componentId, value });
    } else {
      console.warn('[PostMessage] No parent window to send update');
    }
  }

  getConnections() {
    return [];
  }
}

class ComlinkClient {
  constructor() {
    console.log('[Client] Initializing ComlinkClient');
    this.callbacks = new Set();
    this.componentStates = {};
    this.isConnected = false;
    this.pendingUpdates = {};
    this.worker = null;
  }

  async connect() {
    console.log('[Client] Starting connection');
    try {
      if (this.isConnected) {
        console.log('[Client] Already connected');
        return;
      }

      console.log('[Client] About to create worker');
      this.worker = createWorker();
      console.log('[Client] Worker created');

      console.log('[Client] About to initialize Pyodide');
      const result = await this.worker.initializePyodide();
      if (!result.success) {
        throw new Error('Failed to initialize Pyodide');
      }

      this.isConnected = true;
      console.log('[Client] Connection established');
      this._notifySubscribers({ type: 'connection_status', connected: true });

      console.log('[Client] Loading project fs');
      const resp = await fetch('project_fs.json');
      const raw = await resp.json();

      const files = {};
      for (const [path, entry] of Object.entries(raw)) {
        if (entry.type === 'text') {
          files[path] = entry.content;
        } else if (entry.type === 'binary') {
          files[path] = Uint8Array.from(atob(entry.content), (c) => c.charCodeAt(0));
        }
      }

      await this.worker.loadFilesToFS(files);
      console.log('[Client] Project fs loaded');

      const scriptResult = await this.worker.runScript(
        '/project/' + (raw.__entrypoint__ || 'hello.py')
      );

      if (!scriptResult.success) {
        throw new Error('Failed to run initial script');
      }

      this._handleComponentUpdate(scriptResult.components);

      // Process any pending updates
      const pendingCount = Object.keys(this.pendingUpdates).length;
      if (pendingCount > 0) {
        console.log('[Client] Processing pending updates:', pendingCount);
        for (const [componentId, value] of Object.entries(this.pendingUpdates)) {
          await this._sendComponentUpdate(componentId, value);
        }
        this.pendingUpdates = {};
      }
    } catch (error) {
      console.error('[Client] Connection error:', error);
      this.isConnected = false;
      this._notifySubscribers({
        type: 'error',
        content: { message: error.message },
      });
      throw error;
    }
  }

  _handleComponentUpdate(components) {
    console.log('[Client] Handling component update:', components);
    if (components?.rows) {
      components.rows.forEach((row) => {
        row.forEach((component) => {
          if (component.id && 'value' in component) {
            const oldValue = this.componentStates[component.id];
            if (oldValue !== component.value) {
              console.log(`[Client] Component ${component.id} value changed:`, {
                old: oldValue,
                new: component.value,
              });
              this.componentStates[component.id] = component.value;
            }
          }
        });
      });
      this._notifySubscribers({
        type: 'components',
        components: components,
      });
    }
  }

  disconnect() {
    console.log('[Client] Disconnecting');
    if (this.worker) {
      this.worker.shutdown();
      this.worker = null;
      this.isConnected = false;
      this._notifySubscribers({ type: 'connection_status', connected: false });
      console.log('[Client] Disconnected');
    }
  }

  subscribe(callback) {
    console.log('[Client] New subscriber added');
    this.callbacks.add(callback);
    return () => {
      console.log('[Client] Subscriber removed');
      this.callbacks.delete(callback);
    };
  }

  _notifySubscribers(message) {
    console.log('[Client] Notifying subscribers:', message);
    this.callbacks.forEach((callback) => {
      try {
        callback(message);
      } catch (error) {
        console.error('[Client] Error in subscriber callback:', error);
      }
    });
  }

  getComponentState(componentId) {
    return this.componentStates[componentId];
  }

  async updateComponentState(componentId, value) {
    console.log(`[Client] Updating state for component ${componentId}:`, value);
    if (!this.isConnected || !this.worker) {
      console.log('[Client] Not connected, queueing update');
      this.pendingUpdates[componentId] = value;
      throw new Error('Connection not ready');
    }
    return this._sendComponentUpdate(componentId, value);
  }

  async _sendComponentUpdate(componentId, value) {
    console.log(`[Client] Sending component update - ${componentId}:`, value);
    try {
      const result = await this.worker.updateComponent(componentId, value);
      if (!result.success) {
        throw new Error('Component update failed');
      }
      this._handleComponentUpdate(result.components);
      return true;
    } catch (error) {
      console.error('[Client] Error updating component:', error);
      this._notifySubscribers({
        type: 'error',
        content: { message: error.message },
      });
      throw error;
    }
  }

  async loadFilesToFS(files) {
    console.log('[Client] loadFilesToFS', files);
    if (!this.isConnected || !this.worker) {
      throw new Error('Connection not ready');
    }
    return this.worker.loadFilesToFS(files);
  }

  async listFilesInDirectory(directoryPath) {
    console.log('[Client] listFilesInDirectory', directoryPath);
    if (!this.isConnected || !this.worker) {
      throw new Error('Connection not ready');
    }
    return this.worker.listFilesInDirectory(directoryPath);
  }

  // 2. run an arbitrary python script ------------
  async runScript(scriptPath) {
    console.log('[Client] runScript', scriptPath);
    if (!this.isConnected || !this.worker) {
      throw new Error('Connection not ready');
    }
    const result = await this.worker.runScript(scriptPath);
    if (!result.success) {
      throw new Error('Script execution failed');
    }
    this._handleComponentUpdate(result.components);
    return result;
  }

  getConnections() {
    return [];
  }
}

export const createCommunicationLayer = () => {
  // Check if we have a client type specified in window
  const clientType = window.__PRESWALD_CLIENT_TYPE || 'auto';
  console.log('[Communication] Using client type:', clientType);

  // If a specific client type is specified, use it
  if (clientType === 'websocket') {
    console.log('[Communication] Using WebSocketClient');
    return new WebSocketClient();
  } else if (clientType === 'postmessage') {
    console.log('[Communication] Using PostMessageClient');
    return new PostMessageClient();
  } else if (clientType === 'comlink') {
    console.log('[Communication] Using ComlinkClient');
    const client = new ComlinkClient();
    window.__PRESWALD_COMM = client;
    window.__PRESWALD_COMM_READY = true;
    return client;
  }

  // For 'auto' mode, use the original logic
  const isBrowser = window !== window.top;
  console.log(
    '[Communication] Auto-detected environment:',
    isBrowser ? 'browser (iframe)' : 'server (top-level)'
  );

  return isBrowser ? new PostMessageClient() : new WebSocketClient();
};

// Create the communication layer
export const comm = createCommunicationLayer();
