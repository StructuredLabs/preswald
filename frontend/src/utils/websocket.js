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
 * Enhanced connection metrics with ComponentStateManager, MessageEncoder, bulk operations, and transport optimization statistics
 */
  getConnectionMetrics() {
    const baseMetrics = {
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

    // Add transport-specific optimization metrics
    if (this.constructor.name === 'WebSocketClient') {
      baseMetrics.transportOptimization = {
        batchingEnabled: this.batchingEnabled,
        queuedMessages: this.messageQueue.length,
        maxQueueSize: this.maxQueueSize,
        batchSize: this.batchSize,
        batchDelay: this.batchDelay,
        compression: {
          messagesCompressed: this.compressionStats.messagesCompressed,
          avgCompressionRatio: (this.compressionStats.avgCompressionRatio * 100).toFixed(1) + '%'
        }
      };
    } else if (this.constructor.name === 'PostMessageClient') {
      baseMetrics.transportOptimization = {
        batchingEnabled: this.batchingEnabled,
        queuedMessages: this.messageQueue.length,
        maxQueueSize: this.maxQueueSize,
        batchSize: this.batchSize,
        batchDelay: this.batchDelay,
        serialization: {
          messagesOptimized: this.serializationStats.messagesOptimized,
          avgSizeReduction: (this.serializationStats.avgSizeReduction * 100).toFixed(1) + '%'
        }
      };
    }

    return baseMetrics;
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

    // Enhanced transport optimization features
    this.messageQueue = [];
    this.maxQueueSize = 1000;
    this.batchingEnabled = true;
    this.batchTimeout = null;
    this.batchSize = 10;
    this.batchDelay = 16; // ~60fps for UI responsiveness

    // Compression statistics for monitoring
    this.compressionStats = {
      messagesCompressed: 0,
      totalCompressionRatio: 0,
      avgCompressionRatio: 0
    };

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

      // Process any pending` batched messages before disconnecting
      if (this.batchTimeout) {
        clearTimeout(this.batchTimeout);
        this.batchTimeout = null;
        this._processBatchedMessages();
      }

      this.socket.close();
      this.socket = null;
      this._setConnected(false);

      // Clear message queue
      this.messageQueue = [];
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

    // Enhanced batching for better performance
    if (this.batchingEnabled && this.messageQueue.length < this.maxQueueSize) {
      this.messageQueue.push({ componentId, value, timestamp: performance.now() });

      // Schedule batch processing if not already scheduled
      if (!this.batchTimeout) {
        this.batchTimeout = setTimeout(() => {
          this._processBatchedMessages();
        }, this.batchDelay);
      }

      // Process immediately if batch is full
      if (this.messageQueue.length >= this.batchSize) {
        clearTimeout(this.batchTimeout);
        this.batchTimeout = null;
        this._processBatchedMessages();
      }

      return;
    }

    // Fallback to immediate sending
    this._sendImmediateMessage(message, componentId, value);
  }

  _processBatchedMessages() {
    if (this.messageQueue.length === 0) return;

    try {
      // Group messages by component for deduplication
      const stateUpdates = {};
      this.messageQueue.forEach(({ componentId, value }) => {
        stateUpdates[componentId] = value;
      });

      const batchMessage = {
        type: 'component_update',
        states: stateUpdates,
        batch: true,
        count: Object.keys(stateUpdates).length
      };

      this._sendImmediateMessage(batchMessage);

      // Update local states
      Object.entries(stateUpdates).forEach(([componentId, value]) => {
        this.componentStates[componentId] = value;
      });

      console.log(`[WebSocket] Sent batched update: ${Object.keys(stateUpdates).length} components from ${this.messageQueue.length} queued messages`);

      // Clear the queue
      this.messageQueue = [];
      this.batchTimeout = null;

    } catch (error) {
      console.error('[WebSocket] Error processing batched messages:', error);
      // Fallback to individual sends
      this.messageQueue.forEach(({ componentId, value }) => {
        const message = { type: 'component_update', states: { [componentId]: value } };
        this._sendImmediateMessage(message, componentId, value);
      });
      this.messageQueue = [];
      this.batchTimeout = null;
    }
  }

  _sendImmediateMessage(message, componentId = null, value = null) {
    try {
      // Enhanced compression with statistics tracking
      let encodedMessage;
      let originalSize, compressedSize;

      try {
        // Determine if compression should be used
        const jsonString = JSON.stringify(message);
        originalSize = jsonString.length;

        const shouldCompress = originalSize > MessageEncoder.COMPRESSION_THRESHOLD;
        encodedMessage = MessageEncoder.encodeLegacy(message);
        compressedSize = encodedMessage.length;

        // Track compression statistics
        if (shouldCompress && compressedSize < originalSize) {
          this.compressionStats.messagesCompressed++;
          const compressionRatio = (originalSize - compressedSize) / originalSize;
          this.compressionStats.totalCompressionRatio += compressionRatio;
          this.compressionStats.avgCompressionRatio =
            this.compressionStats.totalCompressionRatio / this.compressionStats.messagesCompressed;
        }

      } catch (encodeError) {
        console.warn('[WebSocket] Using legacy JSON encoding:', encodeError.message);
        encodedMessage = JSON.stringify(message);
        compressedSize = encodedMessage.length;
      }

      this.socket.send(encodedMessage);

      if (componentId && value !== null) {
        this.componentStates[componentId] = value;
      }

      // Enhanced logging with compression info
      if (originalSize && compressedSize < originalSize) {
        const compressionRatio = ((originalSize - compressedSize) / originalSize * 100).toFixed(1);
        console.log(`[WebSocket] Sent compressed message: ${originalSize}B → ${compressedSize}B (${compressionRatio}% reduction)`);
      } else {
        console.log('[WebSocket] Sent message:', message.type, compressedSize ? `${compressedSize}B` : '');
      }

    } catch (error) {
      console.error('[WebSocket] Error sending message:', error);
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

    // Enhanced transport optimization features for PostMessage
    this.messageQueue = [];
    this.maxQueueSize = 500; // Smaller queue for PostMessage due to potential parent window limitations
    this.batchingEnabled = true;
    this.batchTimeout = null;
    this.batchSize = 8; // Smaller batch size for PostMessage
    this.batchDelay = 20; // Slightly higher delay for PostMessage

    // Serialization optimization statistics
    this.serializationStats = {
      messagesOptimized: 0,
      totalSizeReduction: 0,
      avgSizeReduction: 0
    };

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

    // Process any pending batched messages before disconnecting
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
      this._processBatchedMessages();
    }

    window.removeEventListener('message', this._handleMessage.bind(this));
    this._setConnected(false);

    // Clear message queue
    this.messageQueue = [];
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
    if (!window.parent) {
      console.warn('[PostMessage] No parent window to send update');
      return;
    }

    // Enhanced batching for better performance
    if (this.batchingEnabled && this.messageQueue.length < this.maxQueueSize) {
      this.messageQueue.push({ componentId, value, timestamp: performance.now() });

      // Schedule batch processing if not already scheduled
      if (!this.batchTimeout) {
        this.batchTimeout = setTimeout(() => {
          this._processBatchedMessages();
        }, this.batchDelay);
      }

      // Process immediately if batch is full
      if (this.messageQueue.length >= this.batchSize) {
        clearTimeout(this.batchTimeout);
        this.batchTimeout = null;
        this._processBatchedMessages();
      }

      return;
    }

    // Fallback to immediate sending
    const message = {
      type: 'component_update',
      id: componentId,
      value,
    };

    this._sendImmediateMessage(message, componentId, value);
  }

  _processBatchedMessages() {
    if (this.messageQueue.length === 0) return;

    try {
      // Group messages by component for deduplication
      const stateUpdates = {};
      this.messageQueue.forEach(({ componentId, value }) => {
        stateUpdates[componentId] = value;
      });

      const batchMessage = {
        type: 'component_update_batch',
        states: stateUpdates,
        count: Object.keys(stateUpdates).length,
        timestamp: performance.now()
      };

      this._sendImmediateMessage(batchMessage);

      // Update local states
      Object.entries(stateUpdates).forEach(([componentId, value]) => {
        this.componentStates[componentId] = value;
      });

      console.log(`[PostMessage] Sent batched update: ${Object.keys(stateUpdates).length} components from ${this.messageQueue.length} queued messages`);

      // Clear the queue
      this.messageQueue = [];
      this.batchTimeout = null;

    } catch (error) {
      console.error('[PostMessage] Error processing batched messages:', error);
      // Fallback to individual sends
      this.messageQueue.forEach(({ componentId, value }) => {
        const message = {
          type: 'component_update',
          id: componentId,
          value,
        };
        this._sendImmediateMessage(message, componentId, value);
      });
      this.messageQueue = [];
      this.batchTimeout = null;
    }
  }

  _sendImmediateMessage(message, componentId = null, value = null) {
    try {
      // Enhanced JSON serialization with optimization tracking
      let encodedMessage;
      let originalSize, optimizedSize;

      try {
        // Optimize message structure for PostMessage
        const optimizedMessage = this._optimizeMessageForPostMessage(message);
        const originalJson = JSON.stringify(message);
        const optimizedJson = JSON.stringify(optimizedMessage);

        originalSize = originalJson.length;
        optimizedSize = optimizedJson.length;

        // Use MessageEncoder for consistent formatting
        encodedMessage = MessageEncoder.encodeLegacy(optimizedMessage);

        // Track optimization statistics
        if (optimizedSize < originalSize) {
          this.serializationStats.messagesOptimized++;
          const sizeReduction = (originalSize - optimizedSize) / originalSize;
          this.serializationStats.totalSizeReduction += sizeReduction;
          this.serializationStats.avgSizeReduction =
            this.serializationStats.totalSizeReduction / this.serializationStats.messagesOptimized;
        }

      } catch (encodeError) {
        console.warn('[PostMessage] Using legacy format:', encodeError.message);
        encodedMessage = message;
        optimizedSize = JSON.stringify(message).length;
      }

      window.parent.postMessage(encodedMessage, '*');

      if (componentId && value !== null) {
        this.componentStates[componentId] = value;
      }

      // Enhanced logging with optimization info
      if (originalSize && optimizedSize < originalSize) {
        const reductionRatio = ((originalSize - optimizedSize) / originalSize * 100).toFixed(1);
        console.log(`[PostMessage] Sent optimized message: ${originalSize}B → ${optimizedSize}B (${reductionRatio}% reduction)`);
      } else {
        console.log('[PostMessage] Sent message:', message.type, optimizedSize ? `${optimizedSize}B` : '');
      }

    } catch (error) {
      console.error('[PostMessage] Error sending message:', error);
      throw error;
    }
  }

  _optimizeMessageForPostMessage(message) {
    // PostMessage-specific optimizations
    const optimized = { ...message };

    // Remove redundant fields for PostMessage transport
    if (optimized.metadata && optimized.metadata.timestamp) {
      // PostMessage doesn't need high-precision timestamps
      optimized.metadata.timestamp = Math.floor(optimized.metadata.timestamp);
    }

    // Optimize value serialization for common types
    if (optimized.value !== undefined) {
      optimized.value = this._optimizeValue(optimized.value);
    }

    if (optimized.states) {
      const optimizedStates = {};
      Object.entries(optimized.states).forEach(([key, value]) => {
        optimizedStates[key] = this._optimizeValue(value);
      });
      optimized.states = optimizedStates;
    }

    return optimized;
  }

  _optimizeValue(value) {
    // Optimize common value types for JSON serialization
    if (typeof value === 'number') {
      // Round floating point numbers to reasonable precision
      return Math.round(value * 1000000) / 1000000;
    }

    if (Array.isArray(value)) {
      // Optimize arrays recursively
      return value.map(item => this._optimizeValue(item));
    }

    if (value && typeof value === 'object') {
      // Remove null/undefined properties
      const optimized = {};
      Object.entries(value).forEach(([key, val]) => {
        if (val !== null && val !== undefined) {
          optimized[key] = this._optimizeValue(val);
        }
      });
      return optimized;
    }

    return value;
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

/**
 * Production-ready Connection Pool Manager
 * Manages multiple connections for load balancing, failover, and performance optimization
 */
class ConnectionPoolManager {
  constructor(config = {}) {
    this.config = {
      maxPoolSize: 3,
      minPoolSize: 1,
      healthCheckInterval: 30000, // 30 seconds
      connectionTimeout: 10000,
      retryAttempts: 3,
      retryDelay: 1000,
      loadBalancingStrategy: 'round-robin', // 'round-robin', 'least-connections', 'performance'
      enableFailover: true,
      ...config
    };

    this.connectionPool = new Map(); // connectionId -> connection
    this.connectionMetrics = new Map(); // connectionId -> metrics
    this.activeConnections = new Set();
    this.currentConnectionIndex = 0;
    this.isShuttingDown = false;
    this.healthCheckTimer = null;

    // Performance tracking
    this.poolMetrics = {
      totalConnections: 0,
      activeConnections: 0,
      failedConnections: 0,
      totalRequests: 0,
      failedRequests: 0,
      avgResponseTime: 0,
      lastHealthCheck: 0
    };

    console.log('[ConnectionPool] Initialized with config:', this.config);
  }

  /**
   * Initialize the connection pool
   */
  async initialize(transportType, transportConfig = {}) {
    console.log(`[ConnectionPool] Initializing pool with ${this.config.minPoolSize} ${transportType} connections`);

    const initPromises = [];
    for (let i = 0; i < this.config.minPoolSize; i++) {
      const connectionId = `${transportType}_${i}_${Date.now()}`;
      initPromises.push(this._createConnection(connectionId, transportType, transportConfig));
    }

    const results = await Promise.allSettled(initPromises);
    const successfulConnections = results.filter(result => result.status === 'fulfilled').length;

    if (successfulConnections === 0) {
      throw new Error('Failed to initialize any connections in the pool');
    }

    console.log(`[ConnectionPool] Initialized ${successfulConnections}/${this.config.minPoolSize} connections`);

    // Start health monitoring
    this._startHealthMonitoring();

    return successfulConnections;
  }

  /**
   * Get an optimal connection from the pool
   */
  getConnection() {
    if (this.isShuttingDown || this.activeConnections.size === 0) {
      throw new Error('Connection pool is not available');
    }

    const activeConnectionsArray = Array.from(this.activeConnections);
    let selectedConnection;

    switch (this.config.loadBalancingStrategy) {
      case 'round-robin':
        selectedConnection = this._getRoundRobinConnection(activeConnectionsArray);
        break;
      case 'least-connections':
        selectedConnection = this._getLeastConnectionsConnection(activeConnectionsArray);
        break;
      case 'performance':
        selectedConnection = this._getPerformanceBasedConnection(activeConnectionsArray);
        break;
      default:
        selectedConnection = this._getRoundRobinConnection(activeConnectionsArray);
    }

    if (!selectedConnection) {
      throw new Error('No healthy connections available in pool');
    }

    this.poolMetrics.totalRequests++;
    this._updateConnectionMetrics(selectedConnection.connectionId, 'request');

    return selectedConnection.client;
  }

  /**
   * Add a new connection to the pool
   */
  async addConnection(transportType, transportConfig = {}) {
    if (this.connectionPool.size >= this.config.maxPoolSize) {
      console.warn('[ConnectionPool] Pool is at maximum capacity');
      return null;
    }

    const connectionId = `${transportType}_${this.connectionPool.size}_${Date.now()}`;
    return await this._createConnection(connectionId, transportType, transportConfig);
  }

  /**
   * Remove a connection from the pool
   */
  async removeConnection(connectionId) {
    const connection = this.connectionPool.get(connectionId);
    if (!connection) {
      console.warn(`[ConnectionPool] Connection ${connectionId} not found`);
      return;
    }

    console.log(`[ConnectionPool] Removing connection ${connectionId}`);

    try {
      await connection.client.disconnect();
    } catch (error) {
      console.error(`[ConnectionPool] Error disconnecting ${connectionId}:`, error);
    }

    this.connectionPool.delete(connectionId);
    this.connectionMetrics.delete(connectionId);
    this.activeConnections.delete(connection);
    this.poolMetrics.totalConnections--;
  }

  /**
   * Get pool statistics
   */
  getPoolMetrics() {
    return {
      ...this.poolMetrics,
      poolSize: this.connectionPool.size,
      activeConnections: this.activeConnections.size,
      connectionDetails: Array.from(this.connectionPool.entries()).map(([id, conn]) => ({
        connectionId: id,
        transport: conn.client.constructor.name,
        isConnected: conn.client.isConnected,
        metrics: this.connectionMetrics.get(id) || {}
      }))
    };
  }

  /**
   * Shutdown the connection pool
   */
  async shutdown() {
    console.log('[ConnectionPool] Shutting down connection pool');
    this.isShuttingDown = true;

    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
    }

    const disconnectPromises = Array.from(this.connectionPool.values()).map(async (connection) => {
      try {
        await connection.client.disconnect();
      } catch (error) {
        console.error(`[ConnectionPool] Error disconnecting ${connection.connectionId}:`, error);
      }
    });

    await Promise.allSettled(disconnectPromises);

    this.connectionPool.clear();
    this.connectionMetrics.clear();
    this.activeConnections.clear();

    console.log('[ConnectionPool] Shutdown complete');
  }

  /**
   * Create a new connection
   * @private
   */
  async _createConnection(connectionId, transportType, transportConfig) {
    console.log(`[ConnectionPool] Creating connection ${connectionId}`);

    try {
      const client = createTransportClient(transportType, transportConfig);
      const startTime = performance.now();

      await client.connect(transportConfig);

      const connectionTime = performance.now() - startTime;
      const connection = {
        connectionId,
        client,
        transportType,
        createdAt: Date.now(),
        connectionTime
      };

      this.connectionPool.set(connectionId, connection);
      this.activeConnections.add(connection);
      this.poolMetrics.totalConnections++;

      // Initialize connection metrics
      this.connectionMetrics.set(connectionId, {
        requests: 0,
        errors: 0,
        avgResponseTime: 0,
        lastActivity: Date.now(),
        connectionTime,
        isHealthy: true
      });

      console.log(`[ConnectionPool] Connection ${connectionId} created successfully in ${connectionTime.toFixed(2)}ms`);
      return connection;

    } catch (error) {
      console.error(`[ConnectionPool] Failed to create connection ${connectionId}:`, error);
      this.poolMetrics.failedConnections++;
      throw error;
    }
  }

  /**
   * Round-robin connection selection
   * @private
   */
  _getRoundRobinConnection(activeConnections) {
    if (activeConnections.length === 0) return null;

    const connection = activeConnections[this.currentConnectionIndex % activeConnections.length];
    this.currentConnectionIndex = (this.currentConnectionIndex + 1) % activeConnections.length;

    return connection;
  }

  /**
   * Least connections selection
   * @private
   */
  _getLeastConnectionsConnection(activeConnections) {
    if (activeConnections.length === 0) return null;

    let selectedConnection = activeConnections[0];
    let minRequests = this.connectionMetrics.get(selectedConnection.connectionId)?.requests || 0;

    for (const connection of activeConnections) {
      const requests = this.connectionMetrics.get(connection.connectionId)?.requests || 0;
      if (requests < minRequests) {
        minRequests = requests;
        selectedConnection = connection;
      }
    }

    return selectedConnection;
  }

  /**
   * Performance-based connection selection
   * @private
   */
  _getPerformanceBasedConnection(activeConnections) {
    if (activeConnections.length === 0) return null;

    let selectedConnection = activeConnections[0];
    let bestScore = this._calculateConnectionScore(selectedConnection.connectionId);

    for (const connection of activeConnections) {
      const score = this._calculateConnectionScore(connection.connectionId);
      if (score > bestScore) {
        bestScore = score;
        selectedConnection = connection;
      }
    }

    return selectedConnection;
  }

  /**
   * Calculate connection performance score
   * @private
   */
  _calculateConnectionScore(connectionId) {
    const metrics = this.connectionMetrics.get(connectionId);
    if (!metrics) return 0;

    // Higher score = better connection
    const latencyFactor = 1000 / Math.max(metrics.avgResponseTime, 1);
    const errorFactor = metrics.requests > 0 ? (1 - (metrics.errors / metrics.requests)) : 1;
    const activityFactor = Math.max(0, 1 - ((Date.now() - metrics.lastActivity) / 60000)); // Decay over 1 minute

    return latencyFactor * 0.4 + errorFactor * 0.4 + activityFactor * 0.2;
  }

  /**
   * Update connection metrics
   * @private
   */
  _updateConnectionMetrics(connectionId, eventType, responseTime = 0) {
    const metrics = this.connectionMetrics.get(connectionId);
    if (!metrics) return;

    switch (eventType) {
      case 'request':
        metrics.requests++;
        metrics.lastActivity = Date.now();
        break;
      case 'response':
        if (responseTime > 0) {
          const totalTime = metrics.avgResponseTime * (metrics.requests - 1) + responseTime;
          metrics.avgResponseTime = totalTime / metrics.requests;
        }
        break;
      case 'error':
        metrics.errors++;
        break;
    }
  }

  /**
   * Start health monitoring
   * @private
   */
  _startHealthMonitoring() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }

    this.healthCheckTimer = setInterval(() => {
      this._performHealthCheck();
    }, this.config.healthCheckInterval);

    console.log(`[ConnectionPool] Health monitoring started (interval: ${this.config.healthCheckInterval}ms)`);
  }

  /**
   * Perform health check on all connections
   * @private
   */
  async _performHealthCheck() {
    if (this.isShuttingDown) return;

    console.log('[ConnectionPool] Performing health check');
    const startTime = performance.now();

    const healthCheckPromises = Array.from(this.connectionPool.entries()).map(async ([connectionId, connection]) => {
      try {
        const isHealthy = connection.client.isConnected &&
          typeof connection.client.getConnectionMetrics === 'function';

        const metrics = this.connectionMetrics.get(connectionId);
        if (metrics) {
          metrics.isHealthy = isHealthy;
        }

        if (!isHealthy) {
          console.warn(`[ConnectionPool] Connection ${connectionId} is unhealthy`);
          this.activeConnections.delete(connection);

          // Attempt to reconnect if failover is enabled
          if (this.config.enableFailover) {
            try {
              await connection.client.connect();
              this.activeConnections.add(connection);
              console.log(`[ConnectionPool] Connection ${connectionId} reconnected successfully`);
            } catch (error) {
              console.error(`[ConnectionPool] Failed to reconnect ${connectionId}:`, error);
            }
          }
        } else {
          this.activeConnections.add(connection);
        }

      } catch (error) {
        console.error(`[ConnectionPool] Health check failed for ${connectionId}:`, error);
        this.activeConnections.delete(connection);
      }
    });

    await Promise.allSettled(healthCheckPromises);

    const healthCheckTime = performance.now() - startTime;
    this.poolMetrics.lastHealthCheck = Date.now();
    this.poolMetrics.activeConnections = this.activeConnections.size;

    console.log(`[ConnectionPool] Health check completed in ${healthCheckTime.toFixed(2)}ms - ${this.activeConnections.size}/${this.connectionPool.size} connections healthy`);
  }
}

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
 * Pooled Communication Client that uses connection pooling for enhanced performance and reliability
 */
class PooledCommunicationClient extends IPreswaldCommunicator {
  constructor(transportType, config = {}) {
    super();
    this.transportType = transportType;
    this.config = config;
    this.connectionPool = null;
    this.isInitialized = false;

    // Aggregate metrics from all pooled connections
    this.aggregateMetrics = {
      totalRequests: 0,
      totalErrors: 0,
      avgResponseTime: 0,
      poolUtilization: 0
    };
  }

  async connect(config = {}) {
    if (this.isInitialized) {
      console.log('[PooledClient] Already initialized');
      return { success: true, message: 'Already connected' };
    }

    console.log('[PooledClient] Initializing connection pool');

    try {
      const poolConfig = {
        maxPoolSize: config.maxPoolSize || 3,
        minPoolSize: config.minPoolSize || 1,
        loadBalancingStrategy: config.loadBalancingStrategy || 'performance',
        enableFailover: config.enableFailover !== false,
        ...config.poolConfig
      };

      this.connectionPool = new ConnectionPoolManager(poolConfig);
      const connectionsCreated = await this.connectionPool.initialize(this.transportType, config);

      this.isInitialized = true;
      this.isConnected = true;

      console.log(`[PooledClient] Initialized with ${connectionsCreated} connections`);
      return { success: true, message: `Connected with ${connectionsCreated} pooled connections` };

    } catch (error) {
      console.error('[PooledClient] Failed to initialize connection pool:', error);
      throw error;
    }
  }

  async disconnect() {
    if (this.connectionPool) {
      console.log('[PooledClient] Shutting down connection pool');
      await this.connectionPool.shutdown();
      this.connectionPool = null;
    }
    this.isInitialized = false;
    this.isConnected = false;
  }

  getComponentState(componentId) {
    if (!this.isInitialized) {
      throw new Error('PooledClient not initialized');
    }

    try {
      const connection = this.connectionPool.getConnection();
      return connection.getComponentState(componentId);
    } catch (error) {
      console.error('[PooledClient] Error getting component state:', error);
      throw error;
    }
  }

  async updateComponentState(componentId, value) {
    if (!this.isInitialized) {
      throw new Error('PooledClient not initialized');
    }

    const startTime = performance.now();

    try {
      const connection = this.connectionPool.getConnection();
      const result = await connection.updateComponentState(componentId, value);

      const responseTime = performance.now() - startTime;
      this._updateAggregateMetrics('success', responseTime);

      return result;
    } catch (error) {
      this._updateAggregateMetrics('error', performance.now() - startTime);
      console.error('[PooledClient] Error updating component state:', error);
      throw error;
    }
  }

  async bulkStateUpdate(updates) {
    if (!this.isInitialized) {
      throw new Error('PooledClient not initialized');
    }

    const startTime = performance.now();

    try {
      const connection = this.connectionPool.getConnection();
      const result = await connection.bulkStateUpdate(updates);

      const responseTime = performance.now() - startTime;
      this._updateAggregateMetrics('success', responseTime);

      return result;
    } catch (error) {
      this._updateAggregateMetrics('error', performance.now() - startTime);
      console.error('[PooledClient] Error in bulk state update:', error);
      throw error;
    }
  }

  subscribe(callback) {
    if (!this.isInitialized) {
      throw new Error('PooledClient not initialized');
    }

    // Subscribe to all connections in the pool
    const unsubscribeFunctions = [];

    for (const connection of this.connectionPool.activeConnections) {
      try {
        const unsubscribe = connection.client.subscribe(callback);
        unsubscribeFunctions.push(unsubscribe);
      } catch (error) {
        console.error('[PooledClient] Error subscribing to connection:', error);
      }
    }

    // Return a function that unsubscribes from all connections
    return () => {
      unsubscribeFunctions.forEach(unsubscribe => {
        try {
          unsubscribe();
        } catch (error) {
          console.error('[PooledClient] Error unsubscribing:', error);
        }
      });
    };
  }

  getConnectionMetrics() {
    if (!this.isInitialized || !this.connectionPool) {
      return {
        isConnected: false,
        transport: 'PooledClient',
        error: 'Not initialized'
      };
    }

    const poolMetrics = this.connectionPool.getPoolMetrics();

    return {
      isConnected: this.isConnected,
      transport: 'PooledClient',
      transportType: this.transportType,
      poolMetrics,
      aggregateMetrics: this.aggregateMetrics,
      connectionCount: poolMetrics.activeConnections,
      poolUtilization: poolMetrics.activeConnections / poolMetrics.poolSize * 100
    };
  }

  getConnections() {
    if (!this.isInitialized || !this.connectionPool) {
      return [];
    }

    return this.connectionPool.getPoolMetrics().connectionDetails;
  }

  _updateAggregateMetrics(type, responseTime) {
    this.aggregateMetrics.totalRequests++;

    if (type === 'error') {
      this.aggregateMetrics.totalErrors++;
    }

    // Update rolling average response time
    const totalTime = this.aggregateMetrics.avgResponseTime * (this.aggregateMetrics.totalRequests - 1) + responseTime;
    this.aggregateMetrics.avgResponseTime = totalTime / this.aggregateMetrics.totalRequests;
  }
}

/**
 * Enhanced factory function to create the appropriate communication client
 * Includes optimized transport selection with environment detection and optional connection pooling
 * 
 * @param {Object} config - Configuration for the communicator
 * @param {string} config.transport - Transport type ('websocket', 'postmessage', 'comlink', 'auto')
 * @param {number} config.connectionTimeout - Connection timeout in ms (default: 10000)
 * @param {boolean} config.enableWorkers - Allow worker-based transports (default: true)
 * @param {boolean} config.enableConnectionPooling - Enable connection pooling (default: false for compatibility)
 * @param {Object} config.poolConfig - Connection pool configuration
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
      enableConnectionPooling: false, // Default to false for backward compatibility
      poolConfig: {
        maxPoolSize: 3,
        minPoolSize: 1,
        loadBalancingStrategy: 'performance'
      },
      ...config
    };

    console.log('[CommunicationFactory] Creating communicator with config:', enhancedConfig);

    // Select optimal transport
    const selectedTransport = TransportSelector.selectOptimalTransport(enhancedConfig);
    console.log('[CommunicationFactory] Selected transport:', selectedTransport);

    let client;

    // Create pooled or single client based on configuration
    if (enhancedConfig.enableConnectionPooling && selectedTransport === TransportType.WEBSOCKET) {
      console.log('[CommunicationFactory] Creating pooled communication client');
      client = new PooledCommunicationClient(selectedTransport, enhancedConfig);
    } else {
      if (enhancedConfig.enableConnectionPooling) {
        console.warn(`[CommunicationFactory] Connection pooling not supported for ${selectedTransport}, falling back to single connection`);
      }
      client = createTransportClient(selectedTransport, enhancedConfig);
    }

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
 * Create a production-ready communication layer with connection pooling enabled
 * Optimized for high-throughput applications serving millions of users
 * 
 * @param {Object} config - Configuration for the pooled communicator
 * @param {number} config.maxPoolSize - Maximum number of connections in pool (default: 3)
 * @param {number} config.minPoolSize - Minimum number of connections in pool (default: 1)
 * @param {string} config.loadBalancingStrategy - Load balancing strategy ('round-robin', 'least-connections', 'performance')
 * @param {boolean} config.enableFailover - Enable automatic failover (default: true)
 * @returns {IPreswaldCommunicator} - Pooled communication interface
 */
export const createProductionCommunicationLayer = (config = {}) => {
  const productionConfig = {
    enableConnectionPooling: true,
    transport: TransportType.WEBSOCKET, // Force WebSocket for production pooling
    poolConfig: {
      maxPoolSize: 3,
      minPoolSize: 2, // Higher minimum for production
      loadBalancingStrategy: 'performance',
      enableFailover: true,
      healthCheckInterval: 15000, // More frequent health checks
      ...config.poolConfig
    },
    connectionTimeout: 8000, // Faster timeout for production
    retryAttempts: 5, // More retries for production
    ...config
  };

  console.log('[ProductionFactory] Creating production communication layer with pooling');
  return createCommunicationLayer(productionConfig);
};

/**
 * Legacy export - maintain backwards compatibility
 * @deprecated Use createCommunicationLayer() directly
 */
export const createCommunicator = createCommunicationLayer;

// Create the communication layer
export const comm = createCommunicationLayer();

/**
 * Export MessageEncoder, ComponentStateManager, ConnectionPoolManager and enhanced communication types for external use
 * Allows applications to use standardized message formatting, bulk state management, transport selection, and connection pooling
 */
export {
  MessageEncoder,
  ComponentStateManager,
  ConnectionPoolManager,
  PooledCommunicationClient,
  MessageType,
  TransportType
};
