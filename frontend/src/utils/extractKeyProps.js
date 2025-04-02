const seenKeys = new Set();

// extractKeyProps.js
export const createExtractKeyProps = () => {
  const seen = new Set();

  const extract = (component, index) => {
    const componentId = component.id || `component-${index}`;
    const { key, ...rest } = {
      key: componentId,
      id: componentId,
      ...component,
    };

    if (seen.has(componentId)) {
      console.warn(`[DynamicComponents] Duplicate key detected: ${componentId}`, component);
    } else {
      seen.add(componentId);
    }

    return [componentId, key, rest];
  };

  extract.reset = () => seen.clear();
  return extract;
};
