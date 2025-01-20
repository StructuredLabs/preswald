import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";

import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import React from "react";
import { cn } from "@/lib/utils";

const UnknownWidget = ({ 
  type = "unknown",
  id,
  className,
  variant = "default" // default, destructive
}) => {
  return (
    <Alert 
      variant={variant === "default" ? "default" : "destructive"}
      className={cn("border-2", className)}
    >
      <ExclamationTriangleIcon className="h-4 w-4" />
      <AlertTitle>Unknown Widget Type</AlertTitle>
      <AlertDescription className="mt-2">
        <div className="space-y-2 text-sm">
          <p>
            The widget type <code className="font-mono bg-muted px-1 py-0.5 rounded">{type}</code> is not recognized.
          </p>
          {id && (
            <p className="text-muted-foreground">
              Widget ID: <code className="font-mono">{id}</code>
            </p>
          )}
          <p className="text-muted-foreground">
            Please check the widget type and ensure it is correctly specified.
          </p>
        </div>
      </AlertDescription>
    </Alert>
  );
};

export default UnknownWidget;
