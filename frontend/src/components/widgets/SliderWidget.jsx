import { useDebouncedCallback } from 'use-debounce';

import React from 'react';

import { Label } from '@/components/ui/label';

import { cn } from '@/lib/utils';

const SliderWidget = ({
  label,
  value = 50,
  min = 0,
  max = 100,
  step = 1,
  onChange,
  id,
  className,
}) => {
  const [localValue, setLocalValue] = React.useState(value);

  const debouncedOnChange = useDebouncedCallback((value) => {
    onChange?.(value);
  }, 100);

  const handleChange = (e) => {
    const newValue = parseFloat(e.target.value);
    setLocalValue(newValue);
    debouncedOnChange(newValue);
  };

  React.useEffect(() => {
    setLocalValue(value);
  }, [value]);

  return (
    <div id={id} className={cn('grid gap-2 w-full max-w-sm mb-4', className)}>
      <div className="flex items-center justify-between">
        <Label
          htmlFor={id}
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          {label}
        </Label>
        <span className="text-sm text-muted-foreground">{localValue}</span>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={localValue}
        onChange={handleChange}
        className="w-full h-2 appearance-none bg-secondary rounded-full cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
      />
    </div>
  );
};

export default SliderWidget;
