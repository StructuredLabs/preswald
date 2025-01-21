import { Card, CardContent } from "@/components/ui/card";

import { Label } from "@/components/ui/label";
import React from "react";
import { Slider } from "@/components/ui/slider";
import { cn } from "@/lib/utils";

const SliderWidget = ({ 
  label, 
  min = 0, 
  max = 100, 
  value = 50, 
  step = 1,
  id, 
  onChange,
  className,
  disabled = false,
  showValue = true,
  showMinMax = true,
  variant = "default" // default, card
}) => {
  const [localValue, setLocalValue] = React.useState(value);

  const handleChange = (e) => {
    const newValue = parseInt(e.target.value, 10);
    setLocalValue(newValue);
  };

  const handleMouseUp = () => {
    if (localValue !== value) {
      console.log("[SliderWidget] Change event:", {
        id,
        value: localValue,
        timestamp: new Date().toISOString()
      });
      onChange?.(localValue);
    }
  };

  React.useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const SliderContent = (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <Label 
          htmlFor={id}
          className={cn(
            "text-sm font-medium",
            disabled && "opacity-50"
          )}
        >
          {label}
        </Label>
        {showValue && (
          <span className="text-sm text-muted-foreground font-medium">
            {localValue}
          </span>
        )}
      </div>
      {/* <Slider
        id={id}
        min={min}
        max={max}
        step={step}
        value={[localValue]}
        onValueChange={handleValueChange}
        disabled={disabled}
        className="w-full text-black"
      /> */}
      <div className="p-4 bg-white">
      <div className="mt-2">
        <input
          id={id}
          name={id}
          type="range"
          min={min}
          max={max}
          value={localValue}
          onChange={handleChange}
          onMouseUp={handleMouseUp}
          onTouchEnd={handleMouseUp}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        />
        </div>
      </div>
      {showMinMax && (
        <div className="flex justify-between">
          <span className="text-sm text-muted-foreground">{min}</span>
          <span className="text-sm text-muted-foreground">{max}</span>
        </div>
      )}
    </div>
  );

  if (variant === "card") {
    return (
      <Card>
        <CardContent className="pt-6">
          {SliderContent}
        </CardContent>
      </Card>
    );
  }

  return SliderContent;
};

export default SliderWidget;
