'use client';

import React from 'react';

import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { cn } from '@/lib/utils';

const SelectboxWidget = ({
  label,
  options = [],
  value,
  id,
  onChange,
  className,
  placeholder = 'Select an option',
  disabled = false,
  error,
  required = false,
  size = 'default', // "sm", "default", "lg"
}) => {
  const handleValueChange = (newValue) => {
    console.log('[SelectboxWidget] Change event:', {
      id,
      oldValue: value,
      newValue: newValue,
      timestamp: new Date().toISOString(),
    });

    try {
      onChange?.(newValue);
      console.log('[SelectboxWidget] State updated successfully:', {
        id,
        value: newValue,
      });
    } catch (error) {
      console.error('[SelectboxWidget] Error updating state:', {
        id,
        error: error.message,
      });
    }
  };

  // Size variants
  const sizeVariants = {
    sm: 'selectbox-size-sm',
    default: 'selectbox-size-default',
    lg: 'selectbox-size-lg',
  };

  return (
    <div className={cn('selectbox-container', className)}>
      {label && (
        <Label
          htmlFor={id}
          className={cn(
            'selectbox-label',
            error && 'selectbox-label-error',
            disabled && 'selectbox-label-disabled'
          )}
        >
          {label}
          {required && <span className="selectbox-required">*</span>}
        </Label>
      )}
      <Select value={value} onValueChange={handleValueChange} disabled={disabled}>
        <SelectTrigger
          id={id}
          className={cn('selectbox-trigger', sizeVariants[size], error && 'selectbox-error')}
        >
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent className="selectbox-content">
          {options.map((option, index) => (
            <SelectItem
              key={index}
              value={option}
              className={cn(
                'selectbox-option',
                size === 'sm' && 'selectbox-option-sm',
                size === 'lg' && 'selectbox-option-lg'
              )}
            >
              {option}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {error && <p className="selectbox-error-message">{error}</p>}
    </div>
  );
};

export default SelectboxWidget;
