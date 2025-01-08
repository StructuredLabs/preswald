import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { debounce, processDataInChunks, sampleData, decompressData } from "../../utils/dataProcessing";
import { FEATURES } from "../../config/features";
import Plot from "react-plotly.js";
import { useInView } from "react-intersection-observer";

const INITIAL_POINTS_THRESHOLD = 1000;
const PROGRESSIVE_LOADING_CHUNK_SIZE = 500;

const DataVisualizationWidget = ({ id, data: rawData, content, error }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [plotError, setPlotError] = useState(null);
  const [processedData, setProcessedData] = useState(null);
  const plotContainerRef = useRef(null);
  const [loadedDataPercentage, setLoadedDataPercentage] = useState(0);
  
  const { ref: inViewRef, inView } = useInView({
    threshold: 0.1,
    triggerOnce: true,
  });

  // Set refs for both intersection observer and plot container
  const setRefs = useCallback(
    (node) => {
      plotContainerRef.current = node;
      inViewRef(node);
    },
    [inViewRef]
  );

  // Decompress and process data if needed
  const data = useMemo(() => {
    if (!rawData) return null;
    
    try {
      // Check if data is compressed
      if (rawData.compressed) {
        return decompressData(rawData.value);
      }
      return rawData;
    } catch (error) {
      console.error("Error processing data:", error);
      setPlotError("Failed to process data");
      return null;
    }
  }, [rawData]);

  // Memoize the plot data processing with progressive loading
  const processPlotData = useCallback((plotData, isInitialLoad = false) => {
    if (!plotData?.data || !Array.isArray(plotData.data)) return plotData;

    const threshold = isInitialLoad ? INITIAL_POINTS_THRESHOLD : FEATURES.DATA_SAMPLING_THRESHOLD;

    return {
      ...plotData,
      data: plotData.data.map(trace => {
        // Deep clone the trace to avoid mutations
        const processedTrace = { ...trace };
        
        // Process numerical arrays for optimization
        ['x', 'y', 'lat', 'lon'].forEach(key => {
          if (Array.isArray(trace[key])) {
            processedTrace[key] = sampleData(trace[key], threshold);
          }
        });

        // Handle marker properties
        if (trace.marker) {
          processedTrace.marker = { ...trace.marker };
          ['size', 'color'].forEach(key => {
            if (Array.isArray(trace.marker[key])) {
              processedTrace.marker[key] = sampleData(trace.marker[key], threshold);
            }
          });
        }

        return processedTrace;
      })
    };
  }, []);

  // Handle data processing and loading
  useEffect(() => {
    if (!inView || !data) return;

    setIsLoading(true);
    setPlotError(null);
    setLoadedDataPercentage(0);

    try {
      // Initial load with fewer points
      const initialData = processPlotData(data, true);
      setProcessedData(initialData);
      setIsLoading(false);

      // Progressive load for full resolution
      if (FEATURES.OPTIMIZED_VISUALIZATION) {
        const traces = data.data || [];
        let totalPoints = 0;
        let processedPoints = 0;

        traces.forEach(trace => {
          ['x', 'y', 'lat', 'lon'].forEach(key => {
            if (Array.isArray(trace[key])) {
              totalPoints += trace[key].length;
            }
          });
        });

        processDataInChunks(
          traces,
          PROGRESSIVE_LOADING_CHUNK_SIZE,
          (chunk, index, total) => {
            setProcessedData(prevData => ({
              ...data,
              data: [
                ...prevData.data.slice(0, index),
                ...chunk,
                ...prevData.data.slice(index + chunk.length)
              ]
            }));

            processedPoints += chunk.reduce((acc, trace) => {
              return acc + (Array.isArray(trace.x) ? trace.x.length : 0);
            }, 0);

            setLoadedDataPercentage((processedPoints / totalPoints) * 100);
          }
        );
      }
    } catch (err) {
      console.error("Error processing plot data:", err);
      setPlotError("Failed to process visualization data");
    }
  }, [inView, data, processPlotData]);

  // Handle resize events with debouncing
  const debouncedResize = useMemo(() => 
    debounce(() => {
      if (plotContainerRef.current) {
        window.Plotly.Plots.resize(plotContainerRef.current);
      }
    }, 150),
    []
  );

  useEffect(() => {
    window.addEventListener('resize', debouncedResize);
    return () => window.removeEventListener('resize', debouncedResize);
  }, [debouncedResize]);

  if (error || plotError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600 font-medium">Error: {error || plotError}</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full" ref={setRefs}>
      {(!inView || isLoading) ? (
        <div className="flex flex-col items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-sm text-gray-600">Loading visualization...</p>
        </div>
      ) : processedData?.data ? (
        <div className="relative w-full" style={{ minHeight: '400px' }}>
          {loadedDataPercentage > 0 && loadedDataPercentage < 100 && (
            <div className="absolute top-0 left-0 right-0 z-10 bg-blue-50 px-4 py-2">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${loadedDataPercentage}%` }}
                ></div>
              </div>
            </div>
          )}
          <Plot
            key={id}
            data={processedData.data}
            layout={{
              ...processedData.layout,
              font: { family: 'Inter, system-ui, sans-serif' },
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              margin: { t: 40, r: 10, l: 60, b: 40 },
              showlegend: true,
              hovermode: 'closest'
            }}
            config={{
              responsive: true,
              displayModeBar: true,
              modeBarButtonsToRemove: ['lasso2d', 'select2d'],
              displaylogo: false,
              ...processedData.config
            }}
            className="w-full h-full"
            useResizeHandler={true}
            style={{ width: '100%', height: '100%' }}
            onError={(err) => {
              console.error("Plotly rendering error:", err);
              setPlotError("Failed to render plot");
            }}
          />
        </div>
      ) : (
        <div className="w-full h-full" ref={plotContainerRef} />
      )}
    </div>
  );
};

export default React.memo(DataVisualizationWidget);


