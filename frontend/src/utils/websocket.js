import { createWorker } from '../backend/service';
import { decode } from '@msgpack/msgpack';

/**
 * Message types used throughout the Preswald communication system
 */
const MessageType = {
  STATE_UPDATE: 'state_update',
  COMPONENT_RENDER: 'component_render',
  COMPONENT_UPDATE: 'component_update',
  COMPONENTS: 'components',
  ERROR: 'error',
  HEARTBEAT: 'heartbeat',
  BULK_UPDATE: 'bulk_update',
  BULK_UPDATE_ACK: 'bulk_update_ack',
  CONNECTION_STATUS: 'connection_status',
  INITIAL_STATE: 'initial_state',
  CONNECTIONS_UPDATE: 'connections_update',
  IMAGE_UPDATE: 'image_update',
  ERRORS_RESULT: 'errors:result',
  CONFIG: 'config'
};

/**
 * MessageEncoder with JSON protocol and optional compression
 * Provides consistent message formatting across all transport types
 */
class MessageEncoder {
  static messageIdCounter = 0;
  static COMPRESSION_THRESHOLD = 1024; // bytes
  static COMPRESSION_PREFIX = 'compressed:';

  /**
   * Encodes a message with metadata and optional compression
   * @param {string} type - Message type from MessageType enum
   * @param {any} payload - Message payload (JSON-serializable)
   * @param {Object} options - Encoding options
   * @returns {string} - Encoded message string
   */
  static encode(type, payload, options = {}) {
    const {
      compressed = false,
      forceCompression = false,
      preserveOriginalFormat = false
    } = options;

    // Handle backwards compatibility - if payload already has type, preserve it
    if (preserveOriginalFormat && payload && typeof payload === 'object' && payload.type) {
      const jsonString = JSON.stringify(payload);
      return this._applyCompression(jsonString, compressed, forceCompression);
    }

    // Create standardized message structure
    const message = {
      type,
      payload,
      metadata: {
        messageId: ++this.messageIdCounter,
        timestamp: performance.now(),
        ...(compressed && { compressed: true })
      }
    };

    const jsonString = JSON.stringify(message);
    return this._applyCompression(jsonString, compressed, forceCompression);
  }

  /**
   * Decodes a message string back to object format
   * @param {string} messageString - Encoded message string
   * @returns {Object} - Decoded message object
   */
  static decode(messageString) {
    if (!messageString || typeof messageString !== 'string') {
      throw new Error('Invalid message string provided');
    }

    try {
      let decodedString = messageString;

      // Handle compressed messages
      if (messageString.startsWith(this.COMPRESSION_PREFIX)) {
        decodedString = this._decompressMessage(messageString);
      }

      const parsed = JSON.parse(decodedString);

      // Validate message structure
      if (!this._isValidMessage(parsed)) {
        // Handle legacy format - if it's a direct object with type, return as-is
        if (parsed && typeof parsed === 'object' && parsed.type) {
          return parsed;
        }
        throw new Error('Invalid message structure');
      }

      return parsed;
    } catch (error) {
      throw new Error(`Failed to decode message: ${error.message}`);
    }
  }

  /**
   * Encodes a message in legacy format for backwards compatibility
   * @param {Object} legacyMessage - Message in original format
   * @returns {string} - JSON string
   */
  static encodeLegacy(legacyMessage) {
    if (!legacyMessage || typeof legacyMessage !== 'object') {
      throw new Error('Invalid legacy message object');
    }

    const jsonString = JSON.stringify(legacyMessage);

    // Apply compression if message is large
    if (jsonString.length > this.COMPRESSION_THRESHOLD) {
      return this._applyCompression(jsonString, true, false);
    }

    return jsonString;
  }

  /**
   * Creates a standardized error message
   * @param {string} message - Error message
   * @param {string} context - Error context
   * @returns {string} - Encoded error message
   */
  static encodeError(message, context = '') {
    return this.encode(MessageType.ERROR, {
      message,
      context,
      timestamp: Date.now()
    });
  }

  /**
   * Creates a standardized state update message
   * @param {string} componentId - Component identifier
   * @param {any} value - New component value
   * @returns {string} - Encoded state update message
   */
  static encodeStateUpdate(componentId, value) {
    return this.encode(MessageType.STATE_UPDATE, {
      component_id: componentId,
      value
    });
  }

  /**
   * Creates a standardized bulk update message
   * @param {Map|Object} updates - Component updates
   * @returns {string} - Encoded bulk update message
   */
  static encodeBulkUpdate(updates) {
    const payload = updates instanceof Map ? Object.fromEntries(updates) : updates;
    return this.encode(MessageType.BULK_UPDATE, {
      states: payload
    }, { compressed: Object.keys(payload).length > 10 });
  }

  /**
   * Applies compression if conditions are met
   * @private
   */
  static _applyCompression(jsonString, compressed, forceCompression) {
    if (forceCompression || (compressed && jsonString.length > this.COMPRESSION_THRESHOLD)) {
      return this._compressMessage(jsonString);
    }
    return jsonString;
  }

  /**
   * base64 encoding
   * TODO: bring compression lib
   * @private
   */
  static _compressMessage(jsonString) {
    try {
      return this.COMPRESSION_PREFIX + btoa(jsonString);
    } catch (error) {
      console.warn('[MessageEncoder] Compression failed, using uncompressed:', error);
      return jsonString;
    }
  }

  /**
   * Decompresses a base64-encoded message
   * @private
   */
  static _decompressMessage(compressedString) {
    try {
      return atob(compressedString.replace(this.COMPRESSION_PREFIX, ''));
    } catch (error) {
      throw new Error(`Decompression failed: ${error.message}`);
    }
  }

  /**
   * Validates message structure
   * @private
   */
  static _isValidMessage(parsed) {
    return parsed &&
      typeof parsed === 'object' &&
      typeof parsed.type === 'string' &&
      parsed.hasOwnProperty('payload') &&
      parsed.metadata &&
      typeof parsed.metadata.messageId === 'number' &&
      typeof parsed.metadata.timestamp === 'number';
  }

  /**
   * Gets encoding statistics for monitoring
   * @returns {Object} - Encoding statistics
   */
  static getStats() {
    return {
      totalMessages: this.messageIdCounter,
      compressionThreshold: this.COMPRESSION_THRESHOLD,
      supportedTypes: Object.values(MessageType)
    };
  }
}

/**
 * Component State Manager for bulk operations
 * Provides efficient state management with change detection, bulk processing,
 * and performance optimizations for high-volume state updates
 */
class ComponentStateManager {
  constructor(config = {}) {
    // Core state storage - using Map for O(1) operations
    this.stateMap = new Map();
    this.subscribers = new Map(); // componentId -> Set<callback>
    this.globalSubscribers = new Set(); // Global state change listeners

    // Performance tracking
    this.metrics = {
      totalUpdates: 0,
      bulkUpdates: 0,
      changeDetections: 0,
      lastBulkSize: 0,
      lastBulkDuration: 0
    };

    // Configuration
    this.config = {
      maxBulkSize: 1000,
      enableMetrics: true,
      deepCompareDepth: 3,
      ...config
    };

    // Change detection optimizations
    this.lastBulkUpdate = 0;
    this.pendingUpdates = new Map();
    this.batchTimeout = null;
  }

  /**
   * Get component state with O(1) lookup
   * @param {string} componentId - Component identifier
   * @param {any} defaultValue - Default value if not found
   * @returns {any} - Component state value
   */
  getState(componentId) {
    if (!componentId || typeof componentId !== 'string') {
      console.warn('[ComponentStateManager] Invalid componentId:', componentId);
      return undefined;
    }

    const state = this.stateMap.get(componentId);
    return state ? state.value : undefined;
  }

  /**
   * Set component state with change detection
   * @param {string} componentId - Component identifier  
   * @param {any} value - New value
   * @returns {boolean} - True if state actually changed
   */
  setState(componentId, value) {
    if (!componentId || typeof componentId !== 'string') {
      throw new Error('Invalid componentId provided');
    }

    const startTime = performance.now();
    const currentState = this.stateMap.get(componentId);
    const hasChanged = this._hasStateChanged(currentState?.value, value);

    if (hasChanged) {
      const newState = {
        value,
        version: (currentState?.version || 0) + 1,
        lastModified: startTime,
        componentId
      };

      this.stateMap.set(componentId, newState);
      this.metrics.totalUpdates++;

      // Notify subscribers
      this._notifyStateChange(componentId, value, currentState?.value);

      if (this.config.enableMetrics) {
        this.metrics.changeDetections++;
      }
    }

    return hasChanged;
  }

  /**
   * Bulk state update with optimized processing
   * @param {Map|Object|Array} updates - Bulk updates in various formats
   * @returns {Object} - Results with metrics and change summary
   */
  bulkSetState(updates) {
    const startTime = performance.now();

    // Normalize updates to Map format for consistent processing
    const updateMap = this._normalizeUpdates(updates);

    if (updateMap.size === 0) {
      return {
        success: true,
        changedCount: 0,
        totalCount: 0,
        duration: 0,
        changes: new Map()
      };
    }

    if (updateMap.size > this.config.maxBulkSize) {
      throw new Error(`Bulk update size ${updateMap.size} exceeds maximum ${this.config.maxBulkSize}`);
    }

    // Process all updates and track changes
    const changes = new Map();
    const notifications = [];
    let changedCount = 0;

    try {
      // Batch process all updates
      for (const [componentId, value] of updateMap) {
        const currentState = this.stateMap.get(componentId);
        const hasChanged = this._hasStateChanged(currentState?.value, value);

        if (hasChanged) {
          const newState = {
            value,
            version: (currentState?.version || 0) + 1,
            lastModified: startTime,
            componentId
          };

          this.stateMap.set(componentId, newState);
          changes.set(componentId, {
            oldValue: currentState?.value,
            newValue: value,
            version: newState.version
          });

          notifications.push({
            componentId,
            newValue: value,
            oldValue: currentState?.value
          });

          changedCount++;
        }
      }

      // Batch notify all changes at once for better performance
      if (notifications.length > 0) {
        this._batchNotifyChanges(notifications);
      }

      const duration = performance.now() - startTime;

      // Update metrics
      if (this.config.enableMetrics) {
        this.metrics.bulkUpdates++;
        this.metrics.totalUpdates += changedCount;
        this.metrics.lastBulkSize = updateMap.size;
        this.metrics.lastBulkDuration = duration;
      }

      console.log(`[ComponentStateManager] Bulk update completed: ${changedCount}/${updateMap.size} changed in ${duration.toFixed(2)}ms`);

      return {
        success: true,
        changedCount,
        totalCount: updateMap.size,
        duration,
        changes
      };

    } catch (error) {
      console.error('[ComponentStateManager] Bulk update failed:', error);
      throw new Error(`Bulk state update failed: ${error.message}`);
    }
  }

  /**
   * Subscribe to state changes for specific component
   * @param {string} componentId - Component to watch
   * @param {Function} callback - Change notification callback
   * @returns {Function} - Unsubscribe function
   */
  subscribe(componentId, callback) {
    if (!this.subscribers.has(componentId)) {
      this.subscribers.set(componentId, new Set());
    }

    this.subscribers.get(componentId).add(callback);

    return () => {
      const componentSubscribers = this.subscribers.get(componentId);
      if (componentSubscribers) {
        componentSubscribers.delete(callback);
        if (componentSubscribers.size === 0) {
          this.subscribers.delete(componentId);
        }
      }
    };
  }

  /**
   * Subscribe to all state changes globally
   * @param {Function} callback - Global change notification callback
   * @returns {Function} - Unsubscribe function
   */
  subscribeGlobal(callback) {
    this.globalSubscribers.add(callback);

    return () => {
      this.globalSubscribers.delete(callback);
    };
  }

  /**
   * Get all current states as a Map
   * @returns {Map} - All component states
   */
  getAllStates() {
    const result = new Map();
    for (const [componentId, state] of this.stateMap) {
      result.set(componentId, state.value);
    }
    return result;
  }

  /**
   * Get performance metrics
   * @returns {Object} - Current metrics
   */
  getMetrics() {
    return {
      ...this.metrics,
      totalComponents: this.stateMap.size,
      subscriberCount: this.subscribers.size,
      globalSubscriberCount: this.globalSubscribers.size
    };
  }

  /**
   * Clear all states and reset manager
   */
  reset() {
    this.stateMap.clear();
    this.subscribers.clear();
    this.globalSubscribers.clear();
    this.pendingUpdates.clear();

    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    // Reset metrics
    this.metrics = {
      totalUpdates: 0,
      bulkUpdates: 0,
      changeDetections: 0,
      lastBulkSize: 0,
      lastBulkDuration: 0
    };
  }

  /**
   * Normalize various update formats to Map
   * @private
   */
  _normalizeUpdates(updates) {
    if (updates instanceof Map) {
      return updates;
    }

    if (Array.isArray(updates)) {
      // Assume array of [componentId, value] tuples
      return new Map(updates);
    }

    if (updates && typeof updates === 'object') {
      return new Map(Object.entries(updates));
    }

    throw new Error('Updates must be Map, Object, or Array format');
  }

  /**
   * Efficient change detection with configurable depth
   * @private
   */
  _hasStateChanged(oldValue, newValue) {
    // Fast equality check
    if (oldValue === newValue) return false;

    // Null/undefined checks
    if (oldValue == null || newValue == null) return oldValue !== newValue;

    // Type mismatch
    if (typeof oldValue !== typeof newValue) return true;

    // Primitive types
    if (typeof oldValue !== 'object') return oldValue !== newValue;

    // Deep comparison for objects (with depth limit for performance)
    return !this._deepEqual(oldValue, newValue, this.config.deepCompareDepth);
  }

  /**
   * Deep equality check with depth limit
   * @private
   */
  _deepEqual(obj1, obj2, maxDepth = 3) {
    if (maxDepth <= 0) return obj1 === obj2;

    if (obj1 === obj2) return true;
    if (obj1 == null || obj2 == null) return obj1 === obj2;
    if (typeof obj1 !== 'object' || typeof obj2 !== 'object') return obj1 === obj2;

    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);

    if (keys1.length !== keys2.length) return false;

    for (const key of keys1) {
      if (!keys2.includes(key)) return false;
      if (!this._deepEqual(obj1[key], obj2[key], maxDepth - 1)) return false;
    }

    return true;
  }

  /**
   * Notify subscribers of state change
   * @private
   */
  _notifyStateChange(componentId, newValue, oldValue) {
    // Notify component-specific subscribers
    const componentSubscribers = this.subscribers.get(componentId);
    if (componentSubscribers) {
      for (const callback of componentSubscribers) {
        try {
          callback(componentId, newValue, oldValue);
        } catch (error) {
          console.error(`[ComponentStateManager] Subscriber error for ${componentId}:`, error);
        }
      }
    }

    // Notify global subscribers
    for (const callback of this.globalSubscribers) {
      try {
        callback(componentId, newValue, oldValue);
      } catch (error) {
        console.error('[ComponentStateManager] Global subscriber error:', error);
      }
    }
  }

  /**
   * Batch notify multiple changes for better performance
   * @private
   */
  _batchNotifyChanges(notifications) {
    // Group notifications by subscriber for efficiency
    const componentNotifications = new Map();
    const globalNotifications = [];

    // Prepare component-specific notifications
    for (const notification of notifications) {
      const { componentId } = notification;
      const subscribers = this.subscribers.get(componentId);

      if (subscribers) {
        if (!componentNotifications.has(componentId)) {
          componentNotifications.set(componentId, []);
        }
        componentNotifications.get(componentId).push(notification);
      }

      globalNotifications.push(notification);
    }

    // Send component-specific batch notifications
    for (const [componentId, componentNotifs] of componentNotifications) {
      const subscribers = this.subscribers.get(componentId);
      if (subscribers) {
        for (const callback of subscribers) {
          try {
            // Send all changes for this component at once
            for (const notif of componentNotifs) {
              callback(notif.componentId, notif.newValue, notif.oldValue);
            }
          } catch (error) {
            console.error(`[ComponentStateManager] Batch subscriber error for ${componentId}:`, error);
          }
        }
      }
    }

    // Send global batch notifications
    for (const callback of this.globalSubscribers) {
      try {
        // Send all changes at once
        for (const notif of globalNotifications) {
          callback(notif.componentId, notif.newValue, notif.oldValue);
        }
      } catch (error) {
        console.error('[ComponentStateManager] Global batch subscriber error:', error);
      }
    }
  }
}

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
    this.componentStates = {}; // Legacy compatibility - will be deprecated
    this.isConnected = false;
    this.pendingUpdates = {};
    this.lastActivity = 0;
    this.connections = [];

    // Initialize ComponentStateManager for enhanced bulk operations
    this.stateManager = new ComponentStateManager({
      maxBulkSize: 1000,
      enableMetrics: true,
      deepCompareDepth: 3
    });

    // Enhanced performance tracking for bulk operations
    this.metrics = {
      messagesReceived: 0,
      messagesSent: 0,
      errors: 0,
      lastLatency: 0,
      bulkUpdatesProcessed: 0,
      lastBulkProcessed: 0,
      lastBulkChanged: 0,
      totalBulkChanges: 0,
      avgBulkProcessingTime: 0
    };

    // Subscribe to state manager changes to maintain legacy compatibility
    this.stateManager.subscribeGlobal((componentId, newValue, oldValue) => {
      this.componentStates[componentId] = newValue;
    });
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
   * Enhanced state management with ComponentStateManager
   */
  getComponentState(componentId) {
    if (!componentId || typeof componentId !== 'string') {
      console.warn(`[${this.constructor.name}] Invalid componentId:`, componentId);
      return undefined;
    }

    // Use ComponentStateManager for enhanced performance
    const value = this.stateManager.getState(componentId);

    // Fallback to legacy componentStates for backwards compatibility
    return value !== undefined ? value : this.componentStates[componentId];
  }

  /**
   * Enhanced bulk update with ComponentStateManager and MessageEncoder support
   */
  async bulkStateUpdate(updates) {
    if (!updates || typeof updates[Symbol.iterator] !== 'function') {
      throw new Error('Updates must be iterable (Map, Array, etc.)');
    }

    const startTime = performance.now();

    try {
      // Use ComponentStateManager for efficient local state management
      const stateResult = this.stateManager.bulkSetState(updates);

      if (stateResult.changedCount === 0) {
        console.log(`[${this.constructor.name}] No state changes detected in bulk update`);
        return {
          results: [],
          totalProcessed: stateResult.totalCount,
          successCount: 0,
          duration: stateResult.duration,
          localChanges: stateResult.changedCount
        };
      }

      // Only send updates for changed states to reduce network traffic
      const changedUpdates = new Map();
      for (const [componentId, changeInfo] of stateResult.changes) {
        changedUpdates.set(componentId, changeInfo.newValue);
      }

      const results = [];
      let successCount = 0;

      // Check if the transport supports native bulk updates
      if (this._sendBulkUpdate && typeof this._sendBulkUpdate === 'function') {
        try {
          const bulkResult = await this._sendBulkUpdate(changedUpdates);
          if (bulkResult.success) {
            // All changes were successfully sent
            for (const componentId of changedUpdates.keys()) {
              results.push({ componentId, success: true });
              successCount++;
            }
          } else {
            throw new Error('Bulk update failed on transport level');
          }
        } catch (error) {
          console.warn(`[${this.constructor.name}] Bulk update failed, falling back to individual updates:`, error);
          // Fall back to individual updates
          return this._fallbackBulkUpdate(changedUpdates, startTime);
        }
      } else {
        // Fall back to individual updates
        return this._fallbackBulkUpdate(changedUpdates, startTime);
      }

      const duration = performance.now() - startTime;
      console.log(`[${this.constructor.name}] Bulk update completed: ${successCount}/${changedUpdates.size} network updates (${stateResult.changedCount}/${stateResult.totalCount} local changes) in ${duration.toFixed(2)}ms`);

      return {
        results,
        totalProcessed: stateResult.totalCount,
        successCount,
        duration,
        localChanges: stateResult.changedCount,
        networkUpdates: changedUpdates.size,
        stateManagerMetrics: this.stateManager.getMetrics()
      };

    } catch (error) {
      console.error(`[${this.constructor.name}] Enhanced bulk update failed:`, error);
      throw error;
    }
  }

  /**
   * Fallback bulk update using individual updates
   * @private
   */
  async _fallbackBulkUpdate(updates, startTime) {
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
    console.log(`[${this.constructor.name}] Fallback bulk update completed: ${successCount}/${results.length} in ${duration.toFixed(2)}ms`);

    return {
      results,
      totalProcessed: results.length,
      successCount,
      duration
    };
  }

  /**
   * Enhanced connection metrics with ComponentStateManager, MessageEncoder, and bulk operation statistics
   */
  getConnectionMetrics() {
    return {
      isConnected: this.isConnected,
      transport: this.constructor.name,
      lastActivity: this.lastActivity,
      pendingUpdates: Object.keys(this.pendingUpdates).length,
      metrics: { ...this.metrics },
      uptime: this.connectTime ? performance.now() - this.connectTime : 0,
      messageEncoder: MessageEncoder.getStats(),
      stateManager: this.stateManager.getMetrics(),
      bulkOperations: {
        totalBulkUpdates: this.metrics.bulkUpdatesProcessed,
        totalBulkChanges: this.metrics.totalBulkChanges,
        avgProcessingTime: this.metrics.avgBulkProcessingTime,
        lastBulkSize: this.metrics.lastBulkProcessed,
        lastBulkChanges: this.metrics.lastBulkChanged,
        bulkEfficiency: this.metrics.lastBulkProcessed > 0 ?
          (this.metrics.lastBulkChanged / this.metrics.lastBulkProcessed * 100).toFixed(1) + '%' : 'N/A'
      }
    };
  }

  /**
 * Enhanced error handling with MessageEncoder support
 */
  _handleError(error, context = '') {
    this.metrics.errors++;
    const errorMessage = `[${this.constructor.name}] ${context ? context + ': ' : ''}${error.message}`;
    console.error(errorMessage, error);

    // Create standardized error message
    const errorPayload = {
      type: 'error',
      content: {
        message: error.message,
        context,
        timestamp: performance.now(),
        transport: this.constructor.name
      }
    };

    this._notifySubscribers(errorPayload);
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
              // Use MessageEncoder for consistent parsing with fallback to legacy
              let data;
              try {
                data = MessageEncoder.decode(event.data);
                // If it's a new format message, extract payload
                if (data.metadata && data.payload) {
                  data = { ...data.payload, type: data.type };
                }
              } catch (decodeError) {
                // Fallback to legacy JSON parsing for backwards compatibility
                console.warn('[WebSocket] Using legacy JSON parsing:', decodeError.message);
                data = JSON.parse(event.data);
              }

              console.log('[WebSocket] Message received:', {
                ...data,
                timestamp: new Date().toISOString(),
              });

              switch (data.type) {
                case 'initial_state':
                  // Use ComponentStateManager for bulk initial state loading
                  if (data.states) {
                    this.stateManager.bulkSetState(data.states);
                    console.log('[WebSocket] Initial states loaded via ComponentStateManager:', Object.keys(data.states).length, 'components');
                  }
                  // Legacy compatibility
                  this.componentStates = { ...data.states };
                  break;

                case 'state_update':
                  if (data.component_id) {
                    // Use ComponentStateManager for individual updates
                    this.stateManager.setState(data.component_id, data.value);
                    console.log('[WebSocket] Component state updated:', {
                      componentId: data.component_id,
                      value: data.value,
                    });
                  }
                  break;

                case 'bulk_update':
                  if (data.states) {
                    // Handle bulk updates efficiently
                    const bulkResult = this.stateManager.bulkSetState(data.states);
                    console.log('[WebSocket] Bulk state update processed:', {
                      totalCount: bulkResult.totalCount,
                      changedCount: bulkResult.changedCount,
                      duration: bulkResult.duration
                    });
                  }
                  break;

                case 'bulk_update_ack':
                  // Handle server acknowledgment of bulk updates
                  console.log('[WebSocket] Bulk update acknowledged by server:', {
                    totalCount: data.total_count,
                    changedCount: data.changed_count,
                    processingTime: data.processing_time,
                    validationErrors: data.validation_errors,
                    success: data.success
                  });

                  // Update connection metrics with server performance data
                  if (this.metrics) {
                    this.metrics.lastLatency = data.processing_time * 1000; // Convert to ms
                    this.metrics.lastBulkProcessed = data.total_count;
                    this.metrics.lastBulkChanged = data.changed_count;
                    this.metrics.bulkUpdatesProcessed++;
                    this.metrics.totalBulkChanges += data.changed_count;

                    // Calculate rolling average of bulk processing times
                    const currentAvg = this.metrics.avgBulkProcessingTime;
                    const count = this.metrics.bulkUpdatesProcessed;
                    this.metrics.avgBulkProcessingTime = ((currentAvg * (count - 1)) + (data.processing_time * 1000)) / count;
                  }
                  break;

                case 'components':
                  if (data.components?.rows) {
                    // Extract state updates from component data for bulk processing
                    const stateUpdates = new Map();
                    data.components.rows.forEach((row) => {
                      row.forEach((component) => {
                        if (component.id && 'value' in component) {
                          stateUpdates.set(component.id, component.value);
                        }
                      });
                    });

                    if (stateUpdates.size > 0) {
                      const bulkResult = this.stateManager.bulkSetState(stateUpdates);
                      console.log('[WebSocket] Component states bulk updated:', {
                        totalCount: bulkResult.totalCount,
                        changedCount: bulkResult.changedCount,
                        duration: bulkResult.duration
                      });
                    }
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
      // Use MessageEncoder for consistent formatting, with legacy fallback
      let encodedMessage;
      try {
        encodedMessage = MessageEncoder.encodeLegacy(message);
      } catch (encodeError) {
        console.warn('[WebSocket] Using legacy JSON encoding:', encodeError.message);
        encodedMessage = JSON.stringify(message);
      }

      this.socket.send(encodedMessage);
      this.componentStates[componentId] = value;
      console.log('[WebSocket] Sent component update:', message);
    } catch (error) {
      console.error('[WebSocket] Error sending component update:', error);
      throw error;
    }
  }

  /**
   * Native bulk update implementation for WebSocket transport
   * @private
   */
  async _sendBulkUpdate(updates) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket connection not open');
    }

    try {
      // Use MessageEncoder for efficient bulk updates
      const encodedMessage = MessageEncoder.encodeBulkUpdate(updates);
      this.socket.send(encodedMessage);
      this.metrics.messagesSent++;

      console.log(`[WebSocket] Sent bulk update for ${updates instanceof Map ? updates.size : Object.keys(updates).length} components`);
      return { success: true };
    } catch (error) {
      console.error('[WebSocket] Error sending bulk update:', error);
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
      // Handle both string and object messages with MessageEncoder support
      if (typeof event.data === 'string') {
        try {
          data = MessageEncoder.decode(event.data);
          // If it's a new format message, extract payload
          if (data.metadata && data.payload) {
            data = { ...data.payload, type: data.type };
          }
        } catch (decodeError) {
          // Fallback to legacy JSON parsing
          console.warn('[PostMessage] Using legacy JSON parsing:', decodeError.message);
          data = JSON.parse(event.data);
        }
      } else {
        data = event.data;
      }
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
        // Use ComponentStateManager for bulk initial state loading
        if (data.states) {
          this.stateManager.bulkSetState(data.states);
          console.log('[PostMessage] Initial states loaded via ComponentStateManager:', Object.keys(data.states).length, 'components');
        }
        // Legacy compatibility
        this.componentStates = { ...data.states };
        this._notifySubscribers(data);
        break;

      case 'state_update':
        if (data.component_id) {
          // Use ComponentStateManager for individual updates
          this.stateManager.setState(data.component_id, data.value);
          console.log('[PostMessage] Component state updated:', {
            componentId: data.component_id,
            value: data.value,
          });
        }
        this._notifySubscribers(data);
        break;

      case 'bulk_update':
        if (data.states) {
          // Handle bulk updates efficiently
          const bulkResult = this.stateManager.bulkSetState(data.states);
          console.log('[PostMessage] Bulk state update processed:', {
            totalCount: bulkResult.totalCount,
            changedCount: bulkResult.changedCount,
            duration: bulkResult.duration
          });
        }
        this._notifySubscribers(data);
        break;

      case 'bulk_update_ack':
        // Handle server acknowledgment of bulk updates
        console.log('[PostMessage] Bulk update acknowledged by server:', {
          totalCount: data.total_count,
          changedCount: data.changed_count,
          processingTime: data.processing_time,
          validationErrors: data.validation_errors,
          success: data.success
        });

        // Update connection metrics with server performance data
        if (this.metrics) {
          this.metrics.lastLatency = data.processing_time * 1000; // Convert to ms
          this.metrics.lastBulkProcessed = data.total_count;
          this.metrics.lastBulkChanged = data.changed_count;
          this.metrics.bulkUpdatesProcessed++;
          this.metrics.totalBulkChanges += data.changed_count;

          // Calculate rolling average of bulk processing times
          const currentAvg = this.metrics.avgBulkProcessingTime;
          const count = this.metrics.bulkUpdatesProcessed;
          this.metrics.avgBulkProcessingTime = ((currentAvg * (count - 1)) + (data.processing_time * 1000)) / count;
        }
        this._notifySubscribers(data);
        break;

      case 'components':
        if (data.components && data.components.rows) {
          // Extract state updates from component data for bulk processing
          const stateUpdates = new Map();
          data.components.rows.forEach((row) => {
            row.forEach((component) => {
              if (component.id && 'value' in component) {
                stateUpdates.set(component.id, component.value);
              }
            });
          });

          if (stateUpdates.size > 0) {
            const bulkResult = this.stateManager.bulkSetState(stateUpdates);
            console.log('[PostMessage] Component states bulk updated:', {
              totalCount: bulkResult.totalCount,
              changedCount: bulkResult.changedCount,
              duration: bulkResult.duration
            });
          }
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
      const message = {
        type: 'component_update',
        id: componentId,
        value,
      };

      // Use MessageEncoder for consistent formatting, with legacy fallback
      let encodedMessage;
      try {
        encodedMessage = MessageEncoder.encodeLegacy(message);
      } catch (encodeError) {
        console.warn('[PostMessage] Using legacy format:', encodeError.message);
        encodedMessage = message;
      }

      window.parent.postMessage(encodedMessage, '*');
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
      // Extract state updates from component data for bulk processing
      const stateUpdates = new Map();
      components.rows.forEach((row) => {
        row.forEach((component) => {
          if (component.id && 'value' in component) {
            stateUpdates.set(component.id, component.value);
          }
        });
      });

      if (stateUpdates.size > 0) {
        const bulkResult = this.stateManager.bulkSetState(stateUpdates);
        console.log('[Client] Component states bulk updated:', {
          totalCount: bulkResult.totalCount,
          changedCount: bulkResult.changedCount,
          duration: bulkResult.duration
        });
      }

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
 * Transport types available for communication
 */
const TransportType = {
  WEBSOCKET: 'websocket',
  POST_MESSAGE: 'postmessage',
  COMLINK: 'comlink',
  AUTO: 'auto'
};

class TransportSelector {
  static selectOptimalTransport(config = {}) {
    const requestedTransport = config.transport || window.__PRESWALD_CLIENT_TYPE || TransportType.AUTO;

    // If specific transport requested, validate and return
    if (requestedTransport !== TransportType.AUTO) {
      return this.validateTransport(requestedTransport, config);
    }

    // Auto-detection logic with enhanced environment analysis
    const environment = this.detectEnvironment();
    const optimalTransport = this.selectForEnvironment(environment, config);

    console.log('[TransportSelector] Environment detected:', environment);
    console.log('[TransportSelector] Selected transport:', optimalTransport);

    return optimalTransport;
  }

  static detectEnvironment() {
    const environment = {
      isIframe: window !== window.top,
      hasWebSocket: typeof WebSocket !== 'undefined',
      hasWorkers: typeof Worker !== 'undefined',
      hasPostMessage: typeof window.postMessage === 'function',
      isSecureContext: window.isSecureContext,
      userAgent: navigator.userAgent,
      connectionType: navigator.connection?.effectiveType || 'unknown'
    };

    // Additional environment checks
    environment.isEmbedded = environment.isIframe || window.location !== window.parent.location;
    environment.supportsModules = 'noModule' in HTMLScriptElement.prototype;
    environment.isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

    return environment;
  }

  static selectForEnvironment(environment, config) {
    // Priority-based selection with fallbacks
    if (environment.isEmbedded && environment.hasPostMessage) {
      return TransportType.POST_MESSAGE;
    }

    if (environment.hasWebSocket && !environment.isEmbedded) {
      return TransportType.WEBSOCKET;
    }

    if (environment.hasWorkers && config.enableWorkers !== false) {
      return TransportType.COMLINK;
    }

    // Fallback to PostMessage if available
    if (environment.hasPostMessage) {
      return TransportType.POST_MESSAGE;
    }

    // Last resort fallback
    console.warn('[TransportSelector] No optimal transport found, defaulting to WebSocket');
    return TransportType.WEBSOCKET;
  }

  static validateTransport(transport, config) {
    const environment = this.detectEnvironment();

    switch (transport) {
      case TransportType.WEBSOCKET:
        if (!environment.hasWebSocket) {
          throw new Error('WebSocket transport not supported in this environment');
        }
        break;
      case TransportType.POST_MESSAGE:
        if (!environment.hasPostMessage) {
          throw new Error('PostMessage transport not supported in this environment');
        }
        break;
      case TransportType.COMLINK:
        if (!environment.hasWorkers) {
          throw new Error('Comlink transport requires Web Worker support');
        }
        break;
      default:
        throw new Error(`Unknown transport type: ${transport}`);
    }

    return transport;
  }
}

/**
 * Enhanced factory function to create the appropriate communication client
 * Includes optimized transport selection with environment detection
 * 
 * @param {Object} config - Configuration for the communicator
 * @param {string} config.transport - Transport type ('websocket', 'postmessage', 'comlink', 'auto')
 * @param {number} config.connectionTimeout - Connection timeout in ms (default: 10000)
 * @param {boolean} config.enableWorkers - Allow worker-based transports (default: true)
 * @returns {IPreswaldCommunicator} - Enhanced communication interface
 */
export const createCommunicationLayer = (config = {}) => {
  const startTime = performance.now();

  try {
    // Enhanced configuration with defaults
    const enhancedConfig = {
      transport: TransportType.AUTO,
      connectionTimeout: 10000,
      enableWorkers: true,
      retryAttempts: 3,
      retryDelay: 1000,
      ...config
    };

    console.log('[CommunicationFactory] Creating communicator with config:', enhancedConfig);

    // Select optimal transport
    const selectedTransport = TransportSelector.selectOptimalTransport(enhancedConfig);
    console.log('[CommunicationFactory] Selected transport:', selectedTransport);

    // Create the appropriate client
    const client = createTransportClient(selectedTransport, enhancedConfig);

    // Validate interface compliance
    if (!(client instanceof IPreswaldCommunicator)) {
      throw new Error(`Created client does not implement IPreswaldCommunicator interface`);
    }

    // Set global references for legacy compatibility
    if (selectedTransport === TransportType.COMLINK) {
      window.__PRESWALD_COMM = client;
      window.__PRESWALD_COMM_READY = true;
    }

    const creationTime = performance.now() - startTime;
    console.log(`[CommunicationFactory] Created ${client.constructor.name} in ${creationTime.toFixed(2)}ms`);

    return client;

  } catch (error) {
    console.error('[CommunicationFactory] Failed to create communication layer:', error);

    // Attempt fallback to basic WebSocket client
    try {
      console.log('[CommunicationFactory] Attempting fallback to WebSocket...');
      const fallbackClient = new WebSocketClient();
      console.warn('[CommunicationFactory] Using fallback WebSocket client');
      return fallbackClient;
    } catch (fallbackError) {
      console.error('[CommunicationFactory] Fallback also failed:', fallbackError);
      throw new Error(`Failed to create communication layer: ${error.message}`);
    }
  }
};

/**
 * Creates the appropriate transport client based on type
 * @private
 */
function createTransportClient(transportType, config) {
  switch (transportType) {
    case TransportType.WEBSOCKET:
      return new WebSocketClient();
    case TransportType.POST_MESSAGE:
      return new PostMessageClient();
    case TransportType.COMLINK:
      return new ComlinkClient();
    default:
      throw new Error(`Unsupported transport type: ${transportType}`);
  }
}

/**
 * Utility function to get optimal transport for current environment
 * Useful for debugging and configuration
 */
export const getOptimalTransport = (config = {}) => {
  return TransportSelector.selectOptimalTransport(config);
};

/**
 * Utility function to detect current environment capabilities
 * Useful for debugging and feature detection
 */
export const detectEnvironment = () => {
  return TransportSelector.detectEnvironment();
};

/**
 * Create a communication layer with specific transport (bypasses auto-detection)
 * Useful for testing and specific deployment scenarios
 */
export const createCommunicationLayerWithTransport = (transport, config = {}) => {
  return createCommunicationLayer({ ...config, transport });
};

/**
 * Legacy export - maintain backwards compatibility
 * @deprecated Use createCommunicationLayer() directly
 */
export const createCommunicator = createCommunicationLayer;

// Create the communication layer
export const comm = createCommunicationLayer();

/**
 * Export MessageEncoder, ComponentStateManager and enhanced communication types for external use
 * Allows applications to use standardized message formatting, bulk state management, and transport selection
 */
export {
  MessageEncoder,
  ComponentStateManager,
  MessageType,
  TransportType
};
