// Utility function to sample data points
export const sampleData = (data, threshold) => {
    if (!Array.isArray(data) || data.length <= threshold) return data;

    const samplingRate = Math.ceil(data.length / threshold);
    return data.filter((_, index) => index % samplingRate === 0);
};

// Process data in chunks
export const processDataInChunks = (data, chunkSize, callback) => {
    let currentIndex = 0;

    const processNextChunk = () => {
        const chunk = data.slice(currentIndex, currentIndex + chunkSize);
        callback(chunk, currentIndex);
        currentIndex += chunkSize;

        if (currentIndex < data.length) {
            requestAnimationFrame(processNextChunk);
        }
    };

    processNextChunk();
};

// Debounce function
export const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}; 