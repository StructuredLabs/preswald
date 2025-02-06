import React from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

import { cn } from '@/lib/utils';

const ProgressWidget = ({
  label,
  value = 0,
  steps,
  className,
  showValue = true,
  size = 'default', // "sm", "default", "lg"
}) => {
  // Ensure value is between 0 and 100
  const normalizedValue = Math.min(Math.max(value, 0), 100);

  // Size variants for the progress bar
  const sizeVariants = {
    sm: 'h-2',
    default: 'h-3',
    lg: 'h-4',
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
          {showValue && (
            <span className="text-sm font-medium text-muted-foreground">
              {Math.round(normalizedValue)}%
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {/* Progress bar */}
        <Progress
          value={normalizedValue}
          className={cn(sizeVariants[size], 'transition-all duration-300')}
        />

        {/* Steps */}
        {steps && steps.length > 0 && (
          <div className="mt-4 grid grid-cols-4 gap-2">
            {steps.map((step, index) => {
              const isActive = index < steps.length * (normalizedValue / 100);
              return (
                <div
                  key={index}
                  className={cn(
                    'text-center text-sm transition-colors duration-200',
                    isActive ? 'text-primary font-medium' : 'text-muted-foreground'
                  )}
                >
                  {step}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ProgressWidget;
