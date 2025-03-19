import React from 'react';

import { Card, CardContent } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const SpinnerWidget = ({
  label = 'Loading...',
  size = 'default', // "sm", "default", "lg"
  variant = 'default', // "default", "card"
  className,
  showLabel = true,
}) => {
  // Size variants for the spinner
  const sizeVariants = {
    sm: 'spinner-size-sm',
    default: 'spinner-size-default',
    lg: 'spinner-size-lg',
  };

  const SpinnerContent = (
    <div className={cn('spinner-container', className)}>
      {showLabel && label && <p className="spinner-label">{label}</p>}
      <div className={cn('spinner-animation', sizeVariants[size])} />
    </div>
  );

  if (variant === 'card') {
    return (
      <Card>
        <CardContent className="spinner-card-content">{SpinnerContent}</CardContent>
      </Card>
    );
  }

  return SpinnerContent;
};

export default SpinnerWidget;
