import { Button } from "@/components/ui/button";
import React from "react";
import { cn } from "@/lib/utils";

const ButtonWidget = ({ 
  label, 
  onClick, 
  variant = "outline",
  size = "default",
  className,
  disabled = false,
  loading = false,
  ...props 
}) => {
  return (
    <Button
      variant={variant}
      size={size}
      onClick={onClick || (() => alert("Button clicked!"))}
      className={cn(className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          {label}
        </div>
      ) : (
        label
      )}
    </Button>
  );
};

export default ButtonWidget;
