import React from 'react';

import { Card, CardContent } from '@/components/ui/card';
import { Label } from '@/components/ui/label';

import { cn } from '@/lib/utils';

const SliderWidget = ({
  label,
  min = 0,
  max = 100,
  value = 50,
  step = 1.0,
  id,
  onChange,
  className,
  disabled = false,
  showValue = true,
  showMinMax = true,
  variant = 'default', // default, card
}) => {
  const [localValue, setLocalValue] = React.useState(value);

  const handleChange = (e) => {
    const newValue = parseFloat(e.target.value, 10);
    setLocalValue(newValue);
  };

  const handleMouseUp = () => {
    if (localValue !== value) {
      console.log('[SliderWidget] Change event:', {
        id,
        value: localValue,
        timestamp: new Date().toISOString(),
      });
      onChange?.(localValue);
    }
  };

  React.useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const SliderContent = (
    <div className={cn('slider-container', className)}>
      <div className="slider-header">
        <Label htmlFor={id} className={cn('slider-label', disabled && 'slider-label-disabled')}>
          {label}
        </Label>
        {showValue && <span className="slider-value">{localValue}</span>}
      </div>
      <div className="slider-wrapper">
        <div className="mt-2">
          <input
            id={id}
            name={id}
            type="range"
            min={min}
            max={max}
            step={step}
            value={localValue}
            onChange={handleChange}
            onMouseUp={handleMouseUp}
            onTouchEnd={handleMouseUp}
            className="slider-track"
          />
        </div>
      </div>
      {showMinMax && (
        <div className="slider-min-max">
          <span className="slider-minmax-label">{min}</span>
          <span className="slider-minmax-label">{max}</span>
        </div>
      )}
    </div>
  );

  if (variant === 'card') {
    return (
      <Card>
        <CardContent className="slider-card-content">{SliderContent}</CardContent>
      </Card>
    );
  }

  return SliderContent;
};

export default SliderWidget;
