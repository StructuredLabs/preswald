import React from 'react';

import { Button } from '@/components/ui/button';

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
  ...props
}) => {
  return (
    <Button
      id={id}
      variant={variant}
      size={size}
      onClick={onClick}
      disabled={disabled || isLoading}
      className={cn('font-medium', isLoading && 'opacity-50 cursor-not-allowed', className)}
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
  );
};

export default ButtonWidget;
