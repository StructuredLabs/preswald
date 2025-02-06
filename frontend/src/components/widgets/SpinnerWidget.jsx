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
    sm: 'w-4 h-4 border-2',
    default: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  const SpinnerContent = (
    <div className={cn('flex flex-col items-center justify-center gap-3 p-4', className)}>
      {showLabel && label && <p className="text-sm font-medium text-muted-foreground">{label}</p>}
      <div
        className={cn(
          'rounded-full animate-spin',
          'border-primary/30 border-t-primary',
          sizeVariants[size]
        )}
      />
    </div>
  );

  if (variant === 'card') {
    return (
      <Card>
        <CardContent className="pt-6">{SpinnerContent}</CardContent>
      </Card>
    );
  }

  return SpinnerContent;
};

export default SpinnerWidget;
