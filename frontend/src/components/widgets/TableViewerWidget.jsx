import { ChevronDown } from 'lucide-react';

import React, { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import { cn } from '@/lib/utils';

const TableViewerWidget = ({
  data = [],
  title = 'Table Viewer',
  className,
  variant = 'default', // default, card
  showTitle = true,
  striped = true,
  dense = false,
  hoverable = true,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!data || data.length === 0) {
    return (
      <Card className={cn('tableviewer-card', className)}>
        <CardContent className="tableviewer-card-content">
          <p className="tableviewer-no-data-text">No data available</p>
        </CardContent>
      </Card>
    );
  }

  const TableContent = (
    <div className={cn('tableviewer-container', className)}>
      <div className="tableviewer-header">
        {showTitle && <h3 className="tableviewer-title">{title}</h3>}
        <Button
          variant="ghost"
          size="sm"
          className="tableviewer-toggle-button"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <ChevronDown
            className={cn('tableviewer-chevron', !isExpanded && 'tableviewer-chevron-rotated')}
          />
        </Button>
      </div>
      <div
        className={cn(
          'tableviewer-table-container',
          isExpanded ? 'tableviewer-expanded' : 'tableviewer-collapsed'
        )}
      >
        <Table>
          <TableHeader>
            <TableRow>
              {Object.keys(data[0]).map((key) => (
                <TableHead key={key} className="tableviewer-header-cell">
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
                  'tableviewer-row',
                  hoverable && 'tableviewer-hoverable',
                  striped && index % 2 === 0 && 'tableviewer-striped',
                  dense ? 'tableviewer-dense' : 'tableviewer-normal'
                )}
              >
                {Object.values(row).map((value, idx) => (
                  <TableCell
                    key={idx}
                    className={cn('tableviewer-cell', dense && 'tableviewer-cell-dense')}
                  >
                    {value !== null && value !== undefined ? value : 'N/A'}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );

  if (variant === 'card') {
    return (
      <Card className={cn('tableviewer-card', className)}>
        {showTitle && (
          <CardHeader className="tableviewer-card-header">
            <CardTitle>{title}</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              className="tableviewer-toggle-button"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              <ChevronDown
                className={cn('tableviewer-chevron', !isExpanded && 'tableviewer-chevron-rotated')}
              />
            </Button>
          </CardHeader>
        )}
        <CardContent
          className={cn(
            isExpanded ? 'tableviewer-card-content-expanded' : 'tableviewer-card-content-collapsed'
          )}
        >
          {TableContent}
        </CardContent>
      </Card>
    );
  }

  return TableContent;
};

export default TableViewerWidget;
