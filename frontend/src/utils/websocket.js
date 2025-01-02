class WebSocketClient {
    constructor() {
        this.callbacks = new Set();
        this.socket = null;
        this.clientId = Math.random().toString(36).substring(7);
        this.isConnecting = false;
        this.componentStates = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.pendingMessages = [];
        this.connections = []; // Store current connections
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

                // Send any pending messages
                while (this.pendingMessages.length > 0) {
                    const msg = this.pendingMessages.shift();
                    this.sendMessage(msg);
                }

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
                        type: data.type,
                        data: data,
                        timestamp: new Date().toISOString()
                    });

                    if (data.type === 'initial_state') {
                        this.componentStates = { ...data.states };
                        console.log("[WebSocket] Initial states loaded:", this.componentStates);
                    }
                    else if (data.type === 'state_update') {
                        const { component_id, value } = data;
                        if (component_id) {
                            this.componentStates[component_id] = value;
                            console.log("[WebSocket] Component state updated:", {
                                componentId: component_id,
                                value: value
                            });
                        }
                    }
                    else if (data.type === 'components') {
                        data.components.forEach(component => {
                            if (component.id && 'value' in component) {
                                this.componentStates[component.id] = component.value;
                                console.log("[WebSocket] Component state updated:", {
                                    componentId: component.id,
                                    value: component.value
                                });
                            }
                        });
                    }
                    else if (data.type === 'connections_update') {
                        // Update the stored connections
                        this.connections = data.connections || [];
                        console.log("[WebSocket] Connections updated:", this.connections);
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
            return;
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

    getComponentState(componentId) {
        return this.componentStates[componentId];
    }

    updateComponentState(componentId, value) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            throw new Error("WebSocket connection not open");
        }

        const message = {
            type: "component_update",
            states: {
                [componentId]: value
            }
        };

        try {
            this.socket.send(JSON.stringify(message));
            console.log("[WebSocket] Sent component update:", message);
        } catch (error) {
            console.error("[WebSocket] Error sending component update:", error);
            throw error;
        }
    }

    getConnections() {
        return this.connections;
    }
}

export const websocket = new WebSocketClient(); 