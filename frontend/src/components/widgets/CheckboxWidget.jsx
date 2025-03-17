import React from 'react';

import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';

import { cn } from '@/lib/utils';

const CheckboxWidget = ({
  label,
  checked = false,
  description,
  id,
  onChange,
  className,
  disabled = false,
}) => {
  const handleCheckedChange = (checked) => {
    console.log('[CheckboxWidget] Change event:', {
      id,
      oldValue: checked,
      newValue: checked,
      timestamp: new Date().toISOString(),
    });

    try {
      onChange?.(checked);
      console.log('[CheckboxWidget] State updated successfully:', {
        id,
        value: checked,
      });
    } catch (error) {
      console.error('[CheckboxWidget] Error updating state:', {
        id,
        error: error.message,
      });
    }
  };

  return (
    <div className={cn('checkbox-container', className)}>
      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={handleCheckedChange}
        disabled={disabled}
      />
      <div className="checkbox-label-container">
        <Label htmlFor={id} className="checkbox-label">
          {label}
        </Label>
        {description && <p className="checkbox-description">{description}</p>}
      </div>
    </div>
  );
};

export default CheckboxWidget;
