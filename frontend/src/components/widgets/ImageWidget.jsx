import React from 'react';

const ImageWidget = ({ id, src, alt = '', className }) => {
  return <img src={src} id={id} alt={alt} className={`image-widget ${className || ''}`} />;
};

export default ImageWidget;
