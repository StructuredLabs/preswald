import React from 'react';
import { AlertTriangle } from 'lucide-react';

import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

const CheckboxWidget = ({
  label,
  checked = false,
  description,
  id,
  onChange,
  className,
  disabled = false,
  error,
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
    <div
      id={id}
      className={cn(
        'checkbox-container relative flex items-center py-2 pl-4 pr-4',
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

      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={handleCheckedChange}
        disabled={disabled}
      />
      <div className="checkbox-label-container ml-3">
        <Label htmlFor={id} className="checkbox-label">
          {label}
        </Label>
        {description && <p className="checkbox-description">{description}</p>}
      </div>
    </div>
  );
};

export default CheckboxWidget;
