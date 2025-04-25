/**
 * Deep comparison utilities for efficient component updates
 */

/**
 * Performs a deep comparison between two values with optimizations for large arrays
 * @param {*} a - First value to compare
 * @param {*} b - Second value to compare
 * @param {Object} options - Comparison options
 * @param {number} options.maxDepth - Maximum recursion depth (default: 5)
 * @param {number} options.sampleSize - Number of items to sample in large arrays (default: 5)
 * @param {number} options.maxArraySize - Size threshold for array sampling (default: 20)
 * @returns {boolean} - True if values are deeply equal, false otherwise
 */
export const isDeepEqual = (a, b, options = {}) => {
  const { depth = 0, maxDepth = 5, maxArraySize = 20, sampleSize = 5 } = options;

  // Handle primitives, null, and undefined
  if (a === b) return true;
  if (a == null || b == null) return a === b;

  // Handle different types
  const typeA = typeof a;
  const typeB = typeof b;
  if (typeA !== typeB) return false;

  // Avoid too deep recursion
  if (depth >= maxDepth) {
    console.warn('Max depth reached in deep comparison, using shallow comparison');
    return JSON.stringify(a) === JSON.stringify(b);
  }

  // Handle arrays with optimizations for large datasets
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;

    // For empty arrays
    if (a.length === 0) return true;

    // For small arrays, compare each element
    if (a.length <= maxArraySize) {
      return a.every((val, i) =>
        isDeepEqual(val, b[i], {
          depth: depth + 1,
          maxDepth,
          maxArraySize,
          sampleSize,
        })
      );
    }

    // For large arrays, use sampling strategy:
    // Check first, middle, last and some distributed samples

    // Generate sample indices - first, last, and evenly distributed points
    const indicesToCheck = [
      0, // First element
      a.length - 1, // Last element
    ];

    // Add middle and distributed samples
    const sectionSize = a.length / (sampleSize - 1);
    for (let i = 1; i < sampleSize - 1; i++) {
      indicesToCheck.push(Math.floor(i * sectionSize));
    }

    // Check all sample indices
    return indicesToCheck.every((i) =>
      isDeepEqual(a[i], b[i], {
        depth: depth + 1,
        maxDepth,
        maxArraySize,
        sampleSize,
      })
    );
  }

  // Handle objects (excluding arrays and null)
  if (typeA === 'object') {
    const keysA = Object.keys(a);
    const keysB = Object.keys(b);

    if (keysA.length !== keysB.length) return false;

    // Check if all keys in a exist in b and have the same values
    return keysA.every((key) => {
      if (!Object.prototype.hasOwnProperty.call(b, key)) return false;
      return isDeepEqual(a[key], b[key], {
        depth: depth + 1,
        maxDepth,
        maxArraySize,
        sampleSize,
      });
    });
  }

  // Handle other types
  return a === b;
};

/**
 * Deep merges two objects or arrays with special handling for component structures
 * - Arrays from source replace arrays in target
 * - Objects are recursively merged
 * - Primitives from source replace those in target
 *
 * @param {Object|Array} target - The target object to merge into
 * @param {Object|Array} source - The source object to merge from
 * @param {Object} options - Merge options
 * @param {number} options.maxDepth - Maximum recursion depth (default: 10)
 * @returns {Object|Array} - The merged result
 */
export const deepMerge = (target, source, options = {}) => {
  const { depth = 0, maxDepth = 10 } = options;

  // Handle edge cases
  if (!source) return target;
  if (!target) return source;

  // Handle arrays - prefer source arrays over target
  if (Array.isArray(source)) {
    return [...source];
  }

  // Handle depth limit
  if (depth >= maxDepth) {
    console.warn('Max depth reached in deep merge, returning source');
    return source;
  }

  // If not objects, return source
  if (typeof target !== 'object' || typeof source !== 'object') {
    return source;
  }

  // For objects, create a new object with merged properties
  const result = { ...target };

  Object.keys(source).forEach((key) => {
    // Skip special internal properties prefixed with underscore
    if (key.startsWith('_')) {
      result[key] = source[key];
      return;
    }

    // Special case handling for nested objects
    if (
      source[key] &&
      typeof source[key] === 'object' &&
      !Array.isArray(source[key]) &&
      result[key] &&
      typeof result[key] === 'object' &&
      !Array.isArray(result[key])
    ) {
      result[key] = deepMerge(result[key], source[key], {
        depth: depth + 1,
        maxDepth,
      });
    } else {
      // For arrays, primitives, or when target doesn't have this key, use source value
      result[key] = source[key];
    }
  });

  return result;
};

/**
 * Gets a list of important properties to compare for a component
 * @param {Object} component - The component to analyze
 * @returns {Array<string>} - Array of property names that should be compared
 */
export const getPropertiesToCompare = (component) => {
  if (!component) return [];

  // Common properties for all components
  const properties = ['data'];

  // Add props if present
  if (component.props) {
    properties.push('props');
  }

  // Add specific properties that components might have
  const extraProps = ['config', 'source', 'layout', 'options', 'image'];

  extraProps.forEach((prop) => {
    if (component[prop] !== undefined) {
      properties.push(prop);
    }
  });

  return properties;
};

/**
 * Determines if two components are equal by comparing their important properties
 * @param {Object} prevComponent - Previous component
 * @param {Object} nextComponent - Next component
 * @returns {boolean} - True if components are equal
 */
export const areComponentsEqual = (prevComponent, nextComponent) => {
  // Early return for identical objects or if either is null/undefined
  if (prevComponent === nextComponent) return true;
  if (!prevComponent || !nextComponent) return false;

  // Always compare basic properties
  if (
    prevComponent.id !== nextComponent.id ||
    prevComponent.type !== nextComponent.type ||
    prevComponent.error !== nextComponent.error ||
    prevComponent.value !== nextComponent.value
  ) {
    return false;
  }

  // Get properties to compare based on component type
  const propertiesToCompare = getPropertiesToCompare(prevComponent);

  // Compare all important properties deeply
  return propertiesToCompare.every((prop) => {
    const prevValue = prevComponent[prop];
    const nextValue = nextComponent[prop];

    // Skip if both values don't exist
    if (prevValue === undefined && nextValue === undefined) {
      return true;
    }

    return isDeepEqual(prevValue, nextValue);
  });
};
