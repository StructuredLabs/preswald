import React, { useEffect, useRef, useState } from "react";

import Plot from "react-plotly.js";

const DataVisualizationWidget = ({ id, data, content, error }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [plotError, setPlotError] = useState(null);
  const plotContainerRef = useRef(null);

  useEffect(() => {
    setIsLoading(false);
    setPlotError(null);

    // If we receive HTML content (from backend's fig.to_html())
    if (typeof content === 'string' && content.includes('<div id="plotly">')) {
      try {
        if (plotContainerRef.current) {
          plotContainerRef.current.innerHTML = content;
          // Execute any scripts that came with the plot
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
    }
  }, [content]);

  if (error || plotError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600 font-medium">Error: {error || plotError}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // If we have direct Plotly data
  if (data?.data && Array.isArray(data.data)) {
    const { data: plotData, layout = {}, config = {} } = data;
    
    // Default config for better UX
    const defaultConfig = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
      displaylogo: false,
      ...config
    };

    // Enhanced layout for better visuals
    const enhancedLayout = {
      font: { family: 'Inter, system-ui, sans-serif' },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      margin: { t: 40, r: 10, l: 60, b: 40 },
      ...layout
    };

    try {
      return (
        <div className="w-full h-full">
          <div className="relative w-full" style={{ minHeight: '400px' }}>
            <Plot
              key={id} // Add key to force re-render on data change
              data={plotData}
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

  // For HTML content from backend
  return (
    <div className="w-full h-full">
      <div 
        ref={plotContainerRef}
        className="relative w-full min-h-[400px] plotly-container"
      />
    </div>
  );
};

export default DataVisualizationWidget;
