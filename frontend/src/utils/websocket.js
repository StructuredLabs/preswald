import { componentStore } from './componentStore';

class WebSocketClient {
    constructor() {
        this.socket = null;
        this.callbacks = new Set();
        this.clientId = Math.random().toString(36).substring(7);
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.connections = [];
        this.pendingUpdates = {}; // Only store latest value for each component
    }

    connect() {
        if (this.isConnecting || (this.socket && this.socket.readyState === WebSocket.OPEN)) {
            console.log("[WebSocket] Already connected or connecting");
            return;
        }

        this.isConnecting = true;
        console.log("[WebSocket] Connecting...");

        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;
            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log("[WebSocket] Connected successfully");
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;

                Object.entries(this.pendingUpdates).forEach(([componentId, value]) => {
                    this._sendComponentUpdate(componentId, value);
                });
                this.pendingUpdates = {};

                this._notifySubscribers({
                    type: "connection_status",
                    connected: true
                });
            };

            this.socket.onclose = (event) => {
                console.log("[WebSocket] Connection closed:", event);
                this.isConnecting = false;
                this.socket = null;
                this._notifySubscribers({
                    type: "connection_status",
                    connected: false
                });
                this._handleReconnect();
            };

            this.socket.onerror = (error) => {
                console.error("[WebSocket] Error:", error);
                this.isConnecting = false;
                this._notifySubscribers({
                    type: "error",
                    content: {
                        message: "WebSocket connection error"
                    }
                });
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log("[WebSocket] Message received:", {
                        ...data,
                        timestamp: new Date().toISOString()
                    });

                    switch (data.type) {
                        case 'inital_state':
                            Object.entries(data.states).forEach(([id, value]) => {
                                componentStore.updateComponent(id, value);
                            });
                            console.log("[WebSocket] Initial states loaded:", componentStore.getAllComponents());
                            break;

                        case 'state_update':
                            if (data.component_id) {
                                componentStore.updateComponent(data.component_id, data.value);
                            }
                            console.log("[WebSocket] Component state updated:", {
                                componentId: data.component_id,
                                value: data.value
                            });
                            break;

                        case 'components':
                            componentStore.setComponents(data.components);
                            break;

                        case 'connections_update':
                            this.connections = data.connections || [];
                            console.log("[WebSocket] Connections updated:", this.connections);
                            break;

                        case 'error':
                            if (data.content.componentId) {
                                // Component-specific error goes to ComponentStore
                                componentStore.setError(data.content.componentId, data.content.message);
                            } else {
                                // General errors get passed to subscribers (App.jsx)
                                this._notifySubscribers(data);
                            }
                            break;
                    }

                    // Notify subscribers
                    this._notifySubscribers(data);
                } catch (error) {
                    console.error("[WebSocket] Error processing message:", error);
                    this._notifySubscribers({
                        type: "error",
                        content: {
                            message: "Error processing server message"
                        }
                    });
                }
            };
        } catch (error) {
            console.error("[WebSocket] Error creating connection:", error);
            this.isConnecting = false;
            this._notifySubscribers({
                type: "error",
                content: {
                    message: "Failed to create WebSocket connection"
                }
            });
        }
    }

    disconnect() {
        if (this.socket) {
            console.log("[WebSocket] Disconnecting...");
            this.socket.close();
            this.socket = null;
        }
    }

    _handleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log("[WebSocket] Max reconnection attempts reached");
            this._notifySubscribers({
                type: "error",
                content: {
                    message: "Failed to reconnect after multiple attempts"
                }
            });
        }

        this.reconnectAttempts++;
        const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);
        console.log(`[WebSocket] Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);

        setTimeout(() => {
            if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
                console.log("[WebSocket] Attempting reconnection...");
                this.connect();
            }
        }, delay);
    }

    subscribe(callback) {
        this.callbacks.add(callback);
        return () => this.callbacks.delete(callback);
    }

    _notifySubscribers(message) {
        this.callbacks.forEach(callback => {
            try {
                callback(message);
            } catch (error) {
                console.error("[WebSocket] Error in subscriber callback:", error);
            }
        });
    }

    updateComponentState(componentId, value) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            // Store update to send when connection is restored
            this.pendingUpdates[componentId] = value;
            const error = new Error("WebSocket connection not open");
            componentStore.setError(componentId, error.message);
            throw error;
        }

        return this._sendComponentUpdate(componentId, value);
    }

    _sendComponentUpdate(componentId, value) {
        const message = {
            type: 'component_update',
            states: {
                [componentId]: value
            }
        };

        try {
            this.socket.send(JSON.stringify(message));
            componentStore.updateComponent(componentId, value);
            console.log("[WebSocket] Sent component update:", message);
        } catch (error) {
            console.error("[WebSocket] Error sending component update:", error);
            componentStore.setError(componentId, error.message);
            throw error;
        }
    }

    getConnections() {
        return this.connections;
    }
}

export const websocket = new WebSocketClient(); 