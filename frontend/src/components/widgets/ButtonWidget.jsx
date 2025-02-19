import { Button } from '@/components/ui/button';
import React from 'react';
import { cn } from '@/lib/utils';

const ButtonWidget = ({
  label,
  onClick,
  variant = 'default',
  size = 'default',
  className,
  disabled = false,
  loading = false,
  ...props
}) => {
  return (
    <Button
      variant={variant}
      size={size}
      onClick={onClick || (() => alert('Button clicked!'))}
      className={cn(
        'w-full sm:w-auto px-2 py-1',
        loading && 'cursor-not-allowed',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <div className="flex items-center justify-center gap-2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          <span>{label}</span>
        </div>
      ) : (
        <span>{label}</span>
      )}
    </Button>
  );
};

export default ButtonWidget;
