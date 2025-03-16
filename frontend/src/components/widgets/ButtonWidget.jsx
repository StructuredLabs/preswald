import React from 'react';

import { Button } from '@/components/ui/button';

import { cn } from '@/lib/utils';

const ButtonWidget = ({
  label,
  onClick,
  variant = 'default',
  size = 'default',
  className,
  disabled = false,
  loading = false,
  toggled = false,
  onToggle,
  ...props
}) => {
  const handleClick = (e) => {
    // Toggle the boolean state if onToggle is provided
    if (onToggle) {
      onToggle(!toggled);
    }

    // Also call the original onClick if provided
    if (onClick) {
      onClick(e);
    } else if (!onToggle) {
      // Only show alert if neither onClick nor onToggle is provided
      alert('Button clicked!');
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleClick}
      className={cn(
        'px-2 py-1',
        loading && 'cursor-not-allowed',
        toggled && 'bg-primary-foreground',
        className
      )}
      disabled={disabled || loading}
      aria-pressed={toggled}
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
