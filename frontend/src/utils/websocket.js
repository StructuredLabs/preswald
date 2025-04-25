import { decode } from '@msgpack/msgpack';

import { deepMerge } from './deepComparison';

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
                  const componentId = data.component_id;
                  const newValue = data.value;

                  this._updateComponentState(componentId, newValue);

                  console.log('[WebSocket] Component state updated from server:', {
                    componentId,
                    valueType: typeof newValue,
                  });
                }
                break;

              case 'components':
                if (data.components?.rows) {
                  data.components.rows.forEach((row) => {
                    row.forEach((component) => {
                      if (component.id) {
                        // Store the entire component structure regardless of type
                        this.componentStates[component.id] = {
                          ...component,
                          // Keep track that this is a complete component, not just a value
                          _isCompleteComponent: true,
                        };

                        console.log('[WebSocket] Stored component:', {
                          id: component.id,
                          type: component.type,
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
    const state = this.componentStates[componentId];
    if (state && state._isCompleteComponent) {
      console.log(`[WebSocket] Get state for ${componentId}`, { type: state.type });
    }
    return state;
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
      console.log('[WebSocket] Sent update:', { componentId });

      // Update the local state
      this._updateComponentState(componentId, value);

      return true;
    } catch (error) {
      console.error('[WebSocket] Error sending update:', error);
      throw error;
    }
  }

  getConnections() {
    return this.connections;
  }

  // Helper method for updating component state consistently
  _updateComponentState(componentId, newValue, source = 'internal') {
    const currentState = this.componentStates[componentId];

    // If we have a complete component, preserve its structure
    if (currentState && currentState._isCompleteComponent) {
      // Update with deep merge to maintain component structure
      let updatedState = deepMerge(currentState, { value: newValue });

      // If the new value is an object with additional properties, merge those too
      if (newValue && typeof newValue === 'object') {
        updatedState = deepMerge(updatedState, newValue);
      }

      this.componentStates[componentId] = updatedState;

      if (source !== 'quiet') {
        console.log(`[WebSocket] Updated component ${componentId} state`, {
          type: currentState.type,
        });
      }
    } else {
      // For simple values, just replace
      this.componentStates[componentId] = newValue;
    }

    return this.componentStates[componentId];
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
    window.addEventListener('message', this._handleMessage.bind(this));

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
          const componentId = data.component_id;
          const newValue = data.value;

          this._updateComponentState(componentId, newValue);

          console.log('[PostMessage] Updated state from server:', {
            componentId,
            valueType: typeof newValue,
          });
        }
        this._notifySubscribers(data);
        break;

      case 'components':
        if (data.components && data.components.rows) {
          data.components.rows.forEach((row) => {
            row.forEach((component) => {
              if (component.id) {
                // Store the entire component structure regardless of type
                this.componentStates[component.id] = {
                  ...component,
                  // Keep track that this is a complete component, not just a value
                  _isCompleteComponent: true,
                };

                console.log('[PostMessage] Stored component:', {
                  id: component.id,
                  type: component.type,
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
    const state = this.componentStates[componentId];
    if (state && state._isCompleteComponent) {
      console.log(`[PostMessage] Get state for ${componentId}`, { type: state.type });
    }
    return state;
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

      // Update the local state
      this._updateComponentState(componentId, value);

      console.log('[PostMessage] Sent update:', { componentId });
    } else {
      console.warn('[PostMessage] No parent window to send update');
    }
  }

  getConnections() {
    return [];
  }

  // Helper method for updating component state consistently
  _updateComponentState(componentId, newValue, source = 'internal') {
    const currentState = this.componentStates[componentId];

    // If we have a complete component, preserve its structure
    if (currentState && currentState._isCompleteComponent) {
      // Update with deep merge to maintain component structure
      let updatedState = deepMerge(currentState, { value: newValue });

      // If the new value is an object with additional properties, merge those too
      if (newValue && typeof newValue === 'object') {
        updatedState = deepMerge(updatedState, newValue);
      }

      this.componentStates[componentId] = updatedState;

      if (source !== 'quiet') {
        console.log(`[PostMessage] Updated component ${componentId} state`, {
          type: currentState.type,
        });
      }
    } else {
      // For simple values, just replace
      this.componentStates[componentId] = newValue;
    }

    return this.componentStates[componentId];
  }
}

export const createCommunicationLayer = () => {
  // Detect environment: server (WebSocket) or browser (PostMessage)
  const isBrowser = window !== window.top;
  console.log(
    '[Communication] Detected environment:',
    isBrowser ? 'browser (iframe)' : 'server (top-level)'
  );

  return isBrowser ? new PostMessageClient() : new WebSocketClient();
};

export const comm = createCommunicationLayer();
