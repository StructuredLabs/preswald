import pako from 'pako';

// Decompress data received from WebSocket
export const decompressData = (compressedData) => {
  try {
    const decompressed = pako.inflate(compressedData);
    const textDecoder = new TextDecoder('utf-8');
    const jsonStr = textDecoder.decode(decompressed);
    return JSON.parse(jsonStr);
  } catch (error) {
    console.error('Error decompressing data:', error);
    return null;
  }
};

// Utility function to sample data points with smart sampling
export const sampleData = (data, threshold) => {
  if (!Array.isArray(data) || data.length <= threshold) return data;

  // Use LTTB (Largest-Triangle-Three-Buckets) algorithm for time series
  if (typeof data[0] === 'number') {
    return lttbDownsample(data, threshold);
  }

  // For categorical or non-numeric data, use regular sampling
  const samplingRate = Math.ceil(data.length / threshold);
  return data.filter((_, index) => index % samplingRate === 0);
};

// LTTB (Largest-Triangle-Three-Buckets) downsampling
function lttbDownsample(data, threshold) {
  if (data.length <= threshold) return data;

  const sampled = new Array(threshold);
  let sampledIndex = 0;
  sampled[sampledIndex++] = data[0]; // Always add the first point

  const bucketSize = (data.length - 2) / (threshold - 2);

  let lastSelectedX = 0;
  let lastSelectedY = data[0];

  for (let i = 0; i < threshold - 2; i++) {
    const bucketStart = Math.floor((i + 0) * bucketSize) + 1;
    const bucketEnd = Math.floor((i + 1) * bucketSize) + 1;

    const avgX = (bucketStart + bucketEnd) / 2;
    let maxArea = -1;
    let maxAreaPoint = data[bucketStart];

    for (let j = bucketStart; j < bucketEnd; j++) {
      // Calculate triangle area
      const area =
        Math.abs(
          (lastSelectedX - avgX) * (data[j] - lastSelectedY) -
            (lastSelectedX - j) * (avgX - lastSelectedY)
        ) * 0.5;

      if (area > maxArea) {
        maxArea = area;
        maxAreaPoint = data[j];
      }
    }

    sampled[sampledIndex++] = maxAreaPoint;
    lastSelectedX = bucketEnd;
    lastSelectedY = maxAreaPoint;
  }

  sampled[sampledIndex] = data[data.length - 1]; // Always add the last point
  return sampled;
}

// Process data in chunks with optimized chunk size
export const processDataInChunks = (data, chunkSize, callback) => {
  if (!Array.isArray(data)) return callback(data);

  const optimalChunkSize = Math.min(chunkSize, Math.max(100, Math.floor(data.length / 10)));

  let currentIndex = 0;
  let isProcessing = false;

  const processNextChunk = () => {
    if (isProcessing || currentIndex >= data.length) return;

    isProcessing = true;
    const chunk = data.slice(currentIndex, currentIndex + optimalChunkSize);

    requestAnimationFrame(() => {
      callback(chunk, currentIndex, data.length);
      currentIndex += optimalChunkSize;
      isProcessing = false;

      if (currentIndex < data.length) {
        processNextChunk();
      }
    });
  };

  processNextChunk();
};

// Enhanced debounce with immediate option
export const debounce = (func, wait, immediate = false) => {
  let timeout;

  return function executedFunction(...args) {
    const context = this;

    const later = () => {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };

    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);

    if (callNow) func.apply(context, args);
  };
};
