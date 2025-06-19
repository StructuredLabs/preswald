import { createWorker } from '../backend/service';
import { decode } from '@msgpack/msgpack';

/**
 * Core interface for all Preswald communication clients
 * Provides a unified API across WebSocket, PostMessage, and Comlink transports
 */
class IPreswaldCommunicator {
  /**
   * Connection lifecycle management
   */
  async connect(config = {}) {
    throw new Error('connect() must be implemented by subclass');
  }

  async disconnect() {
    throw new Error('disconnect() must be implemented by subclass');
  }

  /**
   * State management operations
   */
  getComponentState(componentId) {
    throw new Error('getComponentState() must be implemented by subclass');
  }

  async updateComponentState(componentId, value) {
    throw new Error('updateComponentState() must be implemented by subclass');
  }

  /**
   * Subscription management
   */
  subscribe(callback) {
    throw new Error('subscribe() must be implemented by subclass');
  }

  /**
   * Bulk operations for efficiency (optional, with fallback)
   */
  async bulkStateUpdate(updates) {
    // Default implementation using individual updates
    const results = [];
    for (const [componentId, value] of updates) {
      try {
        await this.updateComponentState(componentId, value);
        results.push({ componentId, success: true });
      } catch (error) {
        results.push({ componentId, success: false, error: error.message });
      }
    }
    return { results, totalProcessed: results.length };
  }

  /**
   * Connection health monitoring
   */
  getConnectionMetrics() {
    return {
      isConnected: this.isConnected || false,
      transport: this.constructor.name,
      lastActivity: this.lastActivity || 0,
      pendingUpdates: Object.keys(this.pendingUpdates || {}).length
    };
  }

  /**
   * Legacy compatibility methods - preserved for backwards compatibility
   */
  getConnections() {
    return this.connections || [];
  }
}

/**
 * Base implementation providing common functionality for all transport types
 * Handles state management, subscription management, and error handling
 */
class BaseCommunicationClient extends IPreswaldCommunicator {
  constructor() {
    super();
    this.callbacks = new Set();
    this.componentStates = {};
    this.isConnected = false;
    this.pendingUpdates = {};
    this.lastActivity = 0;
    this.connections = [];

    // Performance tracking
    this.metrics = {
      messagesReceived: 0,
      messagesSent: 0,
      errors: 0,
      lastLatency: 0
    };
  }

  /**
   * Common subscription management
   */
  subscribe(callback) {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }

    this.callbacks.add(callback);
    console.log(`[${this.constructor.name}] Subscriber added, total: ${this.callbacks.size}`);

    return () => {
      this.callbacks.delete(callback);
      console.log(`[${this.constructor.name}] Subscriber removed, total: ${this.callbacks.size}`);
    };
  }

  /**
   * Common notification system with error handling
   */
  _notifySubscribers(message) {
    this.lastActivity = performance.now();
    this.metrics.messagesReceived++;

    this.callbacks.forEach((callback) => {
      try {
        callback(message);
      } catch (error) {
        console.error(`[${this.constructor.name}] Error in subscriber callback:`, error);
        this.metrics.errors++;
      }
    });
  }

  /**
   * Common state management
   */
  getComponentState(componentId) {
    if (!componentId || typeof componentId !== 'string') {
      console.warn(`[${this.constructor.name}] Invalid componentId:`, componentId);
      return undefined;
    }
    return this.componentStates[componentId];
  }

  /**
   * Enhanced bulk update with optimizations
   */
  async bulkStateUpdate(updates) {
    if (!updates || typeof updates[Symbol.iterator] !== 'function') {
      throw new Error('Updates must be iterable (Map, Array, etc.)');
    }

    const startTime = performance.now();
    const results = [];
    let successCount = 0;

    try {
      for (const [componentId, value] of updates) {
        try {
          await this.updateComponentState(componentId, value);
          results.push({ componentId, success: true });
          successCount++;
        } catch (error) {
          results.push({ componentId, success: false, error: error.message });
          console.error(`[${this.constructor.name}] Bulk update failed for ${componentId}:`, error);
        }
      }
    } catch (error) {
      console.error(`[${this.constructor.name}] Bulk update iteration failed:`, error);
      throw error;
    }

    const duration = performance.now() - startTime;
    console.log(`[${this.constructor.name}] Bulk update completed: ${successCount}/${results.length} in ${duration.toFixed(2)}ms`);

    return {
      results,
      totalProcessed: results.length,
      successCount,
      duration
    };
  }

  /**
   * Enhanced connection metrics
   */
  getConnectionMetrics() {
    return {
      isConnected: this.isConnected,
      transport: this.constructor.name,
      lastActivity: this.lastActivity,
      pendingUpdates: Object.keys(this.pendingUpdates).length,
      metrics: { ...this.metrics },
      uptime: this.connectTime ? performance.now() - this.connectTime : 0
    };
  }

  /**
   * Common error handling
   */
  _handleError(error, context = '') {
    this.metrics.errors++;
    const errorMessage = `[${this.constructor.name}] ${context ? context + ': ' : ''}${error.message}`;
    console.error(errorMessage, error);

    this._notifySubscribers({
      type: 'error',
      content: { message: error.message, context }
    });
  }

  /**
   * Common connection state management
   */
  _setConnected(connected) {
    const wasConnected = this.isConnected;
    this.isConnected = connected;

    if (connected && !wasConnected) {
      this.connectTime = performance.now();
      console.log(`[${this.constructor.name}] Connection established`);
    } else if (!connected && wasConnected) {
      console.log(`[${this.constructor.name}] Connection lost`);
    }

    this._notifySubscribers({
      type: 'connection_status',
      connected,
      timestamp: performance.now()
    });
  }
}

class WebSocketClient extends BaseCommunicationClient {
  constructor() {
    super();
    this.socket = null;
    this.clientId = Math.random().toString(36).substring(7);
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    // Note: callbacks, componentStates, isConnected, pendingUpdates, connections 
    // are now inherited from BaseCommunicationClient
  }

  async connect(config = {}) {
    if (this.isConnecting || (this.socket && this.socket.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] Already connected or connecting');
      return { success: true, message: 'Already connected' };
    }

    this.isConnecting = true;
    console.log('[WebSocket] Connecting...');

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;
      this.socket = new WebSocket(wsUrl);

      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          this.isConnecting = false;
          reject(new Error('Connection timeout'));
        }, config.timeout || 10000);

        this.socket.onopen = () => {
          clearTimeout(timeout);
          console.log('[WebSocket] Connected successfully');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;

          // Process pending updates
          Object.entries(this.pendingUpdates).forEach(([componentId, value]) => {
            this._sendComponentUpdate(componentId, value);
          });
          this.pendingUpdates = {};

          this._setConnected(true);
          resolve({ success: true, message: 'Connected successfully' });
        };

        this.socket.onclose = (event) => {
          clearTimeout(timeout);
          console.log('[WebSocket] Connection closed:', event);
          this.isConnecting = false;
          this.socket = null;
          this._setConnected(false);
          this._handleReconnect();
          if (this.isConnecting) {
            reject(new Error('Connection closed during setup'));
          }
        };

        this.socket.onerror = (error) => {
          clearTimeout(timeout);
          console.error('[WebSocket] Error:', error);
          this.isConnecting = false;
          this._handleError(error, 'Connection error');
          reject(new Error('WebSocket connection error'));
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
            this._handleError(error, 'Message processing');
          }
        };
      });
    } catch (error) {
      console.error('[WebSocket] Error creating connection:', error);
      this.isConnecting = false;
      this._handleError(error, 'Connection creation');
      return { success: false, message: error.message };
    }
  }

  async disconnect() {
    if (this.socket) {
      console.log('[WebSocket] Disconnecting...');
      this.socket.close();
      this.socket = null;
      this._setConnected(false);
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

  // subscribe, _notifySubscribers, getComponentState are inherited from BaseCommunicationClient

  async updateComponentState(componentId, value) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      this.pendingUpdates[componentId] = value;
      throw new Error('WebSocket connection not open');
    }
    this.metrics.messagesSent++;
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

class PostMessageClient extends BaseCommunicationClient {
  constructor() {
    super();
    // Note: callbacks, componentStates, isConnected, pendingUpdates
    // are now inherited from BaseCommunicationClient
  }

  async connect(config = {}) {
    console.log('[PostMessage] Setting up listener...');
    window.addEventListener('message', this._handleMessage.bind(this));

    // Assume connected in browser context
    this._setConnected(true);
    console.log('[PostMessage] Connected successfully');

    // Send pending updates
    Object.entries(this.pendingUpdates).forEach(([componentId, value]) => {
      this._sendComponentUpdate(componentId, value);
    });
    this.pendingUpdates = {};

    return { success: true, message: 'PostMessage connected successfully' };
  }

  async disconnect() {
    console.log('[PostMessage] Disconnecting...');
    window.removeEventListener('message', this._handleMessage.bind(this));
    this._setConnected(false);
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

  // subscribe, _notifySubscribers, getComponentState are inherited from BaseCommunicationClient

  async updateComponentState(componentId, value) {
    if (!this.isConnected) {
      this.pendingUpdates[componentId] = value;
      throw new Error('PostMessage connection not ready');
    }
    this.metrics.messagesSent++;
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

  // getConnections is inherited from BaseCommunicationClient
}

class ComlinkClient extends BaseCommunicationClient {
  constructor() {
    super();
    console.log('[Client] Initializing ComlinkClient');
    this.worker = null;
    // Note: callbacks, componentStates, isConnected, pendingUpdates
    // are now inherited from BaseCommunicationClient
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
      const resp = await fetch('project_fs.json', { cache: 'no-cache' });

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

  async disconnect() {
    console.log('[Client] Disconnecting');
    if (this.worker) {
      this.worker.shutdown();
      this.worker = null;
      this._setConnected(false);
      console.log('[Client] Disconnected');
    }
  }

  // subscribe, _notifySubscribers, getComponentState are inherited from BaseCommunicationClient

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

/**
 * Factory function to create the appropriate communication client
 * Returns a unified IPreswaldCommunicator interface regardless of transport type
 * 
 * @param {Object} config - Optional configuration for the communicator
 * @returns {IPreswaldCommunicator} - Unified communication interface
 */
export const createCommunicationLayer = (config = {}) => {
  // Check if we have a client type specified in window or config
  const clientType = config.transport || window.__PRESWALD_CLIENT_TYPE || 'auto';
  console.log('[Communication] Using client type:', clientType);

  let client;

  // If a specific client type is specified, use it
  if (clientType === 'websocket') {
    console.log('[Communication] Creating WebSocketClient');
    client = new WebSocketClient();
  } else if (clientType === 'postmessage') {
    console.log('[Communication] Creating PostMessageClient');
    client = new PostMessageClient();
  } else if (clientType === 'comlink') {
    console.log('[Communication] Creating ComlinkClient');
    client = new ComlinkClient();
    window.__PRESWALD_COMM = client;
    window.__PRESWALD_COMM_READY = true;
  } else {
    // For 'auto' mode, use environment detection
    const isBrowser = window !== window.top;
    console.log(
      '[Communication] Auto-detected environment:',
      isBrowser ? 'browser (iframe)' : 'server (top-level)'
    );

    client = isBrowser ? new PostMessageClient() : new WebSocketClient();
  }

  // Validate that client implements the interface
  if (!(client instanceof IPreswaldCommunicator)) {
    throw new Error('Created client does not implement IPreswaldCommunicator interface');
  }

  console.log(`[Communication] Created ${client.constructor.name} successfully`);
  return client;
};

/**
 * Legacy export - maintain backwards compatibility
 * @deprecated Use createCommunicationLayer() directly
 */
export const createCommunicator = createCommunicationLayer;

// Create the communication layer
export const comm = createCommunicationLayer();
