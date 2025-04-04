import React from 'react';

const ImageWidget = ({ src, alt = '', className }) => {
  return <img src={src} alt={alt} className={`image-widget ${className || ''}`} />;
};

export default ImageWidget;
