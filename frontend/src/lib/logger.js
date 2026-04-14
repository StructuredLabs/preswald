/**
 * Production-ready logging utility with configurable log levels
 * Automatically disables debug logs in production builds
 */

const LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  NONE: 4
};

// Determine log level based on environment
const getDefaultLogLevel = () => {
  if (typeof process !== 'undefined' && process.env) {
    // Node.js environment
    if (process.env.NODE_ENV === 'production') {
      return LogLevel.WARN;
    }
    if (process.env.NODE_ENV === 'test') {
      return LogLevel.ERROR;
    }
  }

  // Browser environment - check for debug flag
  if (typeof window !== 'undefined') {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('debug')) {
      return LogLevel.DEBUG;
    }
    // Check for production indicators
    if (window.location.hostname !== 'localhost' &&
        !window.location.hostname.includes('127.0.0.1') &&
        !window.location.hostname.includes('dev.')) {
      return LogLevel.WARN;
    }
  }

  return LogLevel.DEBUG;
};

class Logger {
  constructor(namespace = 'App', level = null) {
    this.namespace = namespace;
    this.level = level !== null ? level : getDefaultLogLevel();
  }

  _shouldLog(level) {
    return level >= this.level;
  }

  _formatMessage(level, message) {
    return `[${this.namespace}] ${message}`;
  }

  debug(message, ...args) {
    if (this._shouldLog(LogLevel.DEBUG)) {
      console.debug(this._formatMessage('DEBUG', message), ...args);
    }
  }

  info(message, ...args) {
    if (this._shouldLog(LogLevel.INFO)) {
      console.info(this._formatMessage('INFO', message), ...args);
    }
  }

  warn(message, ...args) {
    if (this._shouldLog(LogLevel.WARN)) {
      console.warn(this._formatMessage('WARN', message), ...args);
    }
  }

  error(message, ...args) {
    if (this._shouldLog(LogLevel.ERROR)) {
      console.error(this._formatMessage('ERROR', message), ...args);
    }
  }

  // Set log level dynamically
  setLevel(level) {
    this.level = level;
  }
}

// Create default logger instance
const defaultLogger = new Logger('App');

// Factory function for creating namespaced loggers
export const createLogger = (namespace) => {
  return new Logger(namespace);
};

// Export default logger methods
export const logger = {
  debug: (...args) => defaultLogger.debug(...args),
  info: (...args) => defaultLogger.info(...args),
  warn: (...args) => defaultLogger.warn(...args),
  error: (...args) => defaultLogger.error(...args),
  setLevel: (level) => defaultLogger.setLevel(level),
  LogLevel
};

export { LogLevel, Logger };
export default logger;
