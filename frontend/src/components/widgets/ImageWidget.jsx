import React from 'react';

import { AspectRatio } from '@/components/ui/aspect-ratio';
import { Card } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const ImageWidget = ({
  src,
  alt = '',
  size = 'medium',
  rounded = true,
  className,
  withCard = false,
  aspectRatio = 1,
  objectFit = 'cover',
}) => {
  // Define size classes based on the provided size prop
  const sizeClasses = {
    small: 'image-widget-small',
    medium: 'image-widget-medium',
    large: 'image-widget-large',
    full: 'image-widget-full',
  };

  const ImageComponent = (
    <div className={cn(sizeClasses[size], className)}>
      <AspectRatio ratio={aspectRatio} className="image-widget-container">
        <img
          src={src}
          alt={alt}
          className={cn(
            'image-widget-img',
            rounded && 'image-widget-rounded',
            objectFit === 'contain' && 'image-widget-object-contain'
          )}
        />
      </AspectRatio>
    </div>
  );

  if (withCard) {
    return (
      <Card
        className={cn(
          'image-widget-card',
          rounded && 'image-widget-rounded',
          sizeClasses[size],
          className
        )}
      >
        {ImageComponent}
      </Card>
    );
  }

  return ImageComponent;
};

export default ImageWidget;
