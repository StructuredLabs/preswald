import React from "react";

/**
 * MapWidget component renders the HTML for a Folium map.
 * Expects a `component` prop containing:
 *   - html: The HTML string of the Folium map
 *   - (optional) id: The component ID
 *   - (optional) style, className, etc.
 */
export default function MapWidget({ component, id }) {
  if (!component || !component.html) {
    return <div>No map data available.</div>;
  }

  return (
    <div
      id={id || component.id || "folium-map"}
      className={component.className || "folium-map"}
      style={{
        width: "100%",
        height: "500px",
        ...(component.style || {})
      }}
      // WARNING: This is safe for folium output, but do not use with untrusted HTML!
      dangerouslySetInnerHTML={{ __html: component.html }}
    />
  );
}