import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

const MatplotlibWidget = ({ id, label, image, className, error }) => {
  return (
    <Card
      id={id}
      className={cn(
        'relative w-full',
        error && 'border-destructive border-2 bg-red-50 rounded-md',
        className
      )}
    >
      {error && (
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="absolute top-2 right-2 text-destructive z-10">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <span>{error.toString()}</span>
          </TooltipContent>
        </Tooltip>
      )}

      {label && <h3 className="text-lg font-medium mb-2">{label}</h3>}
      {error ? (
        <div className="w-full h-48 flex items-center justify-center">
          <span className="text-destructive italic text-sm">Plot unavailable</span>
        </div>
      ) : image ? (
        <img
          src={`data:image/png;base64,${image}`}
          alt="Matplotlib Plot"
          className="w-full"
        />
      ) : (
        <p>No plot available</p>
      )}
    </Card>
  );
};

export default MatplotlibWidget;
