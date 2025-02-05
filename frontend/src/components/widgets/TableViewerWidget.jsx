import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { Button } from "@/components/ui/button";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const TableViewerWidget = ({ 
  data = [], 
  title = "Table Viewer",
  className,
  variant = "default", // default, card
  showTitle = true,
  striped = true,
  dense = false,
  hoverable = true
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!data || data.length === 0) {
    return (
      <Card className={cn("w-full", className)}>
        <CardContent className="flex items-center justify-center py-6">
          <p className="text-sm text-muted-foreground">No data available</p>
        </CardContent>
      </Card>
    );
  }

  const TableContent = (
    <div className={cn("w-full", className)}>
      <div className="flex items-center justify-between mb-2">
        {showTitle && (
          <h3 className="text-lg font-medium">{title}</h3>
        )}
        <Button
          variant="ghost"
          size="sm"
          className="p-0 h-9 w-9 flex items-center justify-center"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <ChevronDown
            className={cn(
              "h-4 w-4 transition-transform duration-200 m-auto",
              isExpanded ? "" : "-rotate-90"
            )}
          />
        </Button>
      </div>
      <div
        className={cn(
          "overflow-auto transition-all duration-200 ease-in-out",
          isExpanded ? "opacity-100 max-h-[2000px]" : "opacity-0 max-h-0"
        )}
      >
        <Table>
          <TableHeader>
            <TableRow>
              {Object.keys(data[0]).map((key) => (
                <TableHead
                  key={key}
                  className="font-medium"
                >
                  {key}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, index) => (
              <TableRow
                key={index}
                className={cn(
                  hoverable && "cursor-pointer hover:bg-muted/50",
                  striped && index % 2 === 0 && "bg-muted/50",
                  dense ? "h-8" : "h-12"
                )}
              >
                {Object.values(row).map((value, idx) => (
                  <TableCell
                    key={idx}
                    className={cn(
                      "p-2 md:p-4",
                      dense && "py-1 text-sm"
                    )}
                  >
                    {value !== null && value !== undefined ? value : "N/A"}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );

  if (variant === "card") {
    return (
      <Card className={cn("w-full", className)}>
        {showTitle && (
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle>{title}</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              className="p-0 h-9 w-9 flex items-center justify-center"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              <ChevronDown
                className={cn(
                  "h-4 w-4 transition-transform duration-200 m-auto",
                  isExpanded ? "" : "-rotate-90"
                )}
              />
            </Button>
          </CardHeader>
        )}
        <CardContent className={cn(
          "transition-all duration-200 ease-in-out p-0",
          isExpanded ? "opacity-100" : "opacity-0 h-0 overflow-hidden"
        )}>
          {TableContent}
        </CardContent>
      </Card>
    );
  }

  return TableContent;
};

export default TableViewerWidget;
