import React from 'react';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import { cn } from '@/lib/utils';

const TextInputWidget = ({
  label,
  placeholder,
  value = '',
  id = 'text-input',
  onChange,
  className,
  error,
  disabled = false,
  required = false,
  type = 'text',
  size = 'default', // "sm", "default", "lg"
  variant = 'default', // "default", "ghost"
}) => {
  const handleChange = (e) => {
    const newValue = e.target.value;
    console.log('[TextInputWidget] Change event:', {
      id,
      oldValue: value,
      newValue: newValue,
      timestamp: new Date().toISOString(),
    });

    try {
      onChange?.(newValue);
      console.log('[TextInputWidget] State updated successfully:', {
        id,
        value: newValue,
      });
    } catch (error) {
      console.error('[TextInputWidget] Error updating state:', {
        id,
        error: error.message,
      });
    }
  };

  // Size variants
  const sizeVariants = {
    sm: 'inputfield-size-sm',
    default: 'inputfield-size-default',
    lg: 'inputfield-size-lg',
  };

  return (
    <div className={cn('inputfield-container', className)}>
      {label && (
        <Label
          htmlFor={id}
          className={cn(
            'inputfield-label',
            error && 'inputfield-error',
            disabled && 'inputfield-disabled'
          )}
        >
          {label}
          {required && <span className="inputfield-required">*</span>}
        </Label>
      )}
      <Input
        type={type}
        id={id}
        name={id}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        className={cn(
          sizeVariants[size],
          variant === 'ghost' && 'inputfield-variant-ghost',
          error && 'inputfield-error-border'
        )}
        aria-invalid={error ? 'true' : undefined}
        required={required}
      />
      {error && <p className="inputfield-error-message">{error}</p>}
    </div>
  );
};

export default TextInputWidget;
