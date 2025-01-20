import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import React from "react";
import { cn } from "@/lib/utils";

const CheckboxWidget = ({ 
  label, 
  checked = false, 
  description, 
  id, 
  onChange,
  className,
  disabled = false 
}) => {
  const handleCheckedChange = (checked) => {
    console.log("[CheckboxWidget] Change event:", {
      id,
      oldValue: checked,
      newValue: checked,
      timestamp: new Date().toISOString()
    });
    
    try {
      onChange?.(checked);
      console.log("[CheckboxWidget] State updated successfully:", {
        id,
        value: checked
      });
    } catch (error) {
      console.error("[CheckboxWidget] Error updating state:", {
        id,
        error: error.message
      });
    }
  };

  return (
    <div className={cn("flex items-start space-x-3 space-y-0", className)}>
      <Checkbox
        id={id}
        checked={checked}
        onCheckedChange={handleCheckedChange}
        disabled={disabled}
      />
      <div className="space-y-1 leading-none">
        <Label
          htmlFor={id}
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          {label}
        </Label>
        {description && (
          <p className="text-sm text-muted-foreground">
            {description}
          </p>
        )}
      </div>
    </div>
  );
};

export default CheckboxWidget;
