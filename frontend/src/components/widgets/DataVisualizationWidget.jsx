import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { debounce, processDataInChunks, sampleData } from "../../utils/dataProcessing";

import { FEATURES } from "../../config/features";
import Plot from "react-plotly.js";

const DataVisualizationWidget = ({ id, data, content, error }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [plotError, setPlotError] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [processedData, setProcessedData] = useState(null);
  const plotContainerRef = useRef(null);
  const observerRef = useRef(null);

  // Memoize the plot data processing
  const processPlotData = useCallback((plotData) => {
    if (!plotData?.data || !Array.isArray(plotData.data)) return plotData;

    return {
      ...plotData,
      data: plotData.data.map(trace => ({
        ...trace,
        x: FEATURES.OPTIMIZED_VISUALIZATION 
          ? sampleData(trace.x, FEATURES.DATA_SAMPLING_THRESHOLD)
          : trace.x,
        y: FEATURES.OPTIMIZED_VISUALIZATION 
          ? sampleData(trace.y, FEATURES.DATA_SAMPLING_THRESHOLD)
          : trace.y,
      }))
    };
  }, []);

  // Memoize the processed data
  const memoizedData = useMemo(() => {
    if (!data) return null;
    return processPlotData(data);
  }, [data, processPlotData]);

  // Setup Intersection Observer for lazy loading
  useEffect(() => {
    if (!FEATURES.OPTIMIZED_VISUALIZATION) {
      setIsVisible(true);
      return;
    }

    const options = {
      root: null,
      rootMargin: '50px',
      threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      });
    }, options);

    if (plotContainerRef.current) {
      observer.observe(plotContainerRef.current);
    }

    observerRef.current = observer;
    return () => observer.disconnect();
  }, []);

  // Handle data processing and loading
  useEffect(() => {
    if (!isVisible) return;

    setIsLoading(true);
    setPlotError(null);

    if (typeof content === 'string' && content.includes('<div id="plotly">')) {
      try {
        if (plotContainerRef.current) {
          plotContainerRef.current.innerHTML = content;
          const scripts = plotContainerRef.current.getElementsByTagName('script');
          Array.from(scripts).forEach(script => {
            const newScript = document.createElement('script');
            Array.from(script.attributes).forEach(attr => {
              newScript.setAttribute(attr.name, attr.value);
            });
            newScript.appendChild(document.createTextNode(script.innerHTML));
            script.parentNode.replaceChild(newScript, script);
          });
        }
      } catch (err) {
        setPlotError("Failed to render Plotly visualization");
        console.error("Plot rendering error:", err);
      }
    } else if (memoizedData?.data) {
      if (FEATURES.OPTIMIZED_VISUALIZATION) {
        processDataInChunks(
          memoizedData.data,
          FEATURES.PROGRESSIVE_LOADING_CHUNK_SIZE,
          (chunk) => {
            setProcessedData(prevData => ({
              ...memoizedData,
              data: [...(prevData?.data || []), ...chunk]
            }));
          }
        );
      } else {
        setProcessedData(memoizedData);
      }
    }

    setIsLoading(false);
  }, [isVisible, content, memoizedData]);

  // Handle resize events with debouncing
  const debouncedResize = useMemo(() => 
    debounce(() => {
      if (plotContainerRef.current) {
        window.Plotly.Plots.resize(plotContainerRef.current);
      }
    }, FEATURES.RESIZE_DEBOUNCE_MS),
    []
  );

  useEffect(() => {
    if (FEATURES.OPTIMIZED_VISUALIZATION) {
      window.addEventListener('resize', debouncedResize);
      return () => window.removeEventListener('resize', debouncedResize);
    }
  }, [debouncedResize]);

  if (error || plotError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600 font-medium">Error: {error || plotError}</p>
      </div>
    );
  }

  if (!isVisible || isLoading) {
    return (
      <div className="flex items-center justify-center h-64" ref={plotContainerRef}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (processedData?.data) {
    const { layout = {}, config = {} } = processedData;
    
    const defaultConfig = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
      displaylogo: false,
      ...config
    };

    const enhancedLayout = {
      font: { family: 'Inter, system-ui, sans-serif' },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      margin: { t: 40, r: 10, l: 60, b: 40 },
      ...layout
    };

    try {
      return (
        <div className="w-full h-full" ref={plotContainerRef}>
          <div className="relative w-full" style={{ minHeight: '400px' }}>
            <Plot
              key={id}
              data={processedData.data}
              layout={enhancedLayout}
              config={defaultConfig}
              className="w-full h-full"
              useResizeHandler={true}
              style={{ width: '100%', height: '100%' }}
              onError={(err) => {
                console.error("Plotly rendering error:", err);
                setPlotError("Failed to render plot");
              }}
            />
          </div>
        </div>
      );
    } catch (err) {
      console.error("Error rendering Plotly component:", err);
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600 font-medium">Error rendering plot: {err.message}</p>
        </div>
      );
    }
  }

  return (
    <div className="w-full h-full">
      <div 
        ref={plotContainerRef}
        className="relative w-full min-h-[400px] plotly-container"
      />
    </div>
  );
};

export default React.memo(DataVisualizationWidget);


