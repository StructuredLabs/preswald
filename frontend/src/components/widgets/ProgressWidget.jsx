'use client';

import React from 'react';

import { Progress } from '@/components/ui/progress';

const ProgressWidget = ({ id, value = 0, label }) => {
  // Ensure value is between 0 and 100
  const normalizedValue = Math.min(Math.max(parseFloat(value) || 0, 0), 100);

  return (
    <div id={id} className="w-full space-y-2">
      {label && (
        <div className="flex justify-between text-sm">
          <span>{label}</span>
          <span>{Math.round(normalizedValue)}%</span>
        </div>
      )}
      <Progress value={normalizedValue} />
    </div>
  );
};

export default ProgressWidget;
