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
  ...props
}) => {
  return (
    <Button
      variant={variant}
      size={size}
      onClick={onClick || (() => alert('Button clicked!'))}
      className={cn('button-container', loading && 'button-disabled', className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <div className="button-loading">
          <div className="button-spinner" />
          <span>{label}</span>
        </div>
      ) : (
        <span>{label}</span>
      )}
    </Button>
  );
};

export default ButtonWidget;
