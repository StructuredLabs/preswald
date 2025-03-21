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
    sm: 'progress-size-sm',
    default: 'progress-size-default',
    lg: 'progress-size-lg',
  };

  return (
    <Card className={cn('progress-container', className)}>
      <CardHeader className="progress-header">
        <div className="progress-header-content">
          <CardTitle className="progress-label">{label}</CardTitle>
          {showValue && <span className="progress-value">{Math.round(normalizedValue)}%</span>}
        </div>
      </CardHeader>
      <CardContent>
        {/* Progress bar */}
        <Progress value={normalizedValue} className={cn('progress-bar', sizeVariants[size])} />

        {/* Steps */}
        {steps && steps.length > 0 && (
          <div className="progress-steps">
            {steps.map((step, index) => {
              const isActive = index < steps.length * (normalizedValue / 100);
              return (
                <div
                  key={index}
                  className={cn(
                    'progress-step',
                    isActive ? 'progress-step-active' : 'progress-step-inactive'
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
