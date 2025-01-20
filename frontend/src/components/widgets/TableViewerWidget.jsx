import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import React from "react";
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
    <div className={cn("w-full overflow-auto", className)}>
      {showTitle && (
        <h3 className="text-lg font-medium mb-4">{title}</h3>
      )}
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
  );

  if (variant === "card") {
    return (
      <Card className={cn("w-full", className)}>
        {showTitle && (
          <CardHeader>
            <CardTitle>{title}</CardTitle>
          </CardHeader>
        )}
        <CardContent className="p-0">
          {TableContent}
        </CardContent>
      </Card>
    );
  }

  return TableContent;
};

export default TableViewerWidget;
