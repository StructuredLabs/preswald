'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { Label } from "@/components/ui/label";
import React from 'react';
import { cn } from "@/lib/utils";

const SelectboxWidget = ({ 
  label, 
  options = [], 
  value, 
  id, 
  onChange,
  className,
  placeholder = "Select an option",
  disabled = false,
  error,
  required = false,
  size = "default" // "sm", "default", "lg"
}) => {
  const handleValueChange = (newValue) => {
    console.log("[SelectboxWidget] Change event:", {
      id,
      oldValue: value,
      newValue: newValue,
      timestamp: new Date().toISOString()
    });

    try {
      onChange?.(newValue);
      console.log("[SelectboxWidget] State updated successfully:", {
        id,
        value: newValue
      });
    } catch (error) {
      console.error("[SelectboxWidget] Error updating state:", {
        id,
        error: error.message
      });
    }
  };

  // Size variants
  const sizeVariants = {
    sm: "h-8 text-xs",
    default: "h-10 text-sm",
    lg: "h-12 text-base"
  };

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <Label 
          htmlFor={id}
          className={cn(
            "text-sm font-medium",
            error && "text-destructive",
            disabled && "opacity-50"
          )}
        >
          {label}
          {required && <span className="text-destructive ml-1">*</span>}
        </Label>
      )}
      <Select
        value={value}
        onValueChange={handleValueChange}
        disabled={disabled}
      >
        <SelectTrigger
          id={id}
          className={cn(
            sizeVariants[size],
            error && "border-destructive focus:ring-destructive"
          )}
        >
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {options.map((option, index) => (
            <SelectItem
              key={index}
              value={option}
              className={cn(
                "cursor-pointer",
                size === "sm" && "text-xs py-1.5",
                size === "lg" && "text-base py-2.5"
              )}
            >
              {option}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {error && (
        <p className="text-xs text-destructive mt-1">
          {error}
        </p>
      )}
    </div>
  );
};

export default SelectboxWidget;
