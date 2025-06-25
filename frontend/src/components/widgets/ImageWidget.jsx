import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

const ImageWidget = ({ id, src, alt = '', className, error }) => {
  return (
    <div
      className={cn(
        'relative inline-block',
        error && 'border-destructive border-2 bg-red-50 p-1 rounded-md'
      )}
      id={id}
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

      {error ? (
        <div className="w-full h-full flex items-center justify-center py-6">
          <span className="text-destructive italic text-sm">Image unavailable</span>
        </div>
      ) : (
        <img
          src={src}
          alt={alt}
          className={cn('image-widget', className)}
        />
      )}
    </div>
  );
};

export default ImageWidget;
