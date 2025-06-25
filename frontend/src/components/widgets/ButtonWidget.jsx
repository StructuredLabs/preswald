import React from 'react';
import { AlertTriangle } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

const ButtonWidget = ({
  id,
  children,
  onClick,
  isLoading,
  disabled,
  variant = 'default',
  size = 'default',
  className,
  error,
  ...props
}) => {
  return (
    <div
      className={cn(
        'relative inline-block',
        error && 'border-destructive border-2 bg-red-50 p-1 rounded-md'
      )}
    >
      {error && (
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="absolute top-1 right-1 text-destructive">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <span>{error.toString()}</span>
          </TooltipContent>
        </Tooltip>
      )}

      <Button
        id={id}
        variant={variant}
        size={size}
        onClick={onClick}
        disabled={disabled || isLoading}
        className={cn(
          'font-medium',
          isLoading && 'opacity-50 cursor-not-allowed',
          className
        )}
        {...props}
      >
        {isLoading ? (
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            {children}
          </div>
        ) : (
          children
        )}
      </Button>
    </div>
  );
};

export default ButtonWidget;

