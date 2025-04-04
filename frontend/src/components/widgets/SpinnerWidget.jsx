import React from 'react';

import { Card, CardContent } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const SpinnerWidget = ({
  label = 'Loading...',
  variant = 'default',
  className,
  showLabel = true,
}) => {
  const SpinnerContent = (
    <div className={cn('flex flex-col items-center gap-2 p-4', className)}>
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      {showLabel && label && <p className="text-sm text-muted-foreground">{label}</p>}
    </div>
  );

  if (variant === 'card') {
    return (
      <Card>
        <CardContent>{SpinnerContent}</CardContent>
      </Card>
    );
  }

  return SpinnerContent;
};

export default SpinnerWidget;
