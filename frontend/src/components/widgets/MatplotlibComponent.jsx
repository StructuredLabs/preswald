import React from 'react';

const MatplotlibComponent = ({ data }) => {
  const { image, format } = data;
  if (format === 'svg') {
    // For SVG, we need to decode and render it as HTML
    const decodedSvg = atob(image);
    return (
      <div
        className="w-full overflow-hidden rounded-lg shadow-sm"
        dangerouslySetInnerHTML={{ __html: decodedSvg }}
      />
    );
  }

  // For PNG and other formats, use img tag
  return (
    <div className="w-full overflow-hidden rounded-lg shadow-sm">
      <img src={`data:image/${format};base64,${image}`} alt="Matplotlib Plot" />
    </div>
  );
};

export default MatplotlibComponent;
