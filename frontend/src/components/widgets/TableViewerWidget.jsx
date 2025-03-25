import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { AgGridReact } from 'ag-grid-react';
import { ChevronDown } from 'lucide-react';

import React, { useMemo, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const TableViewerWidget = ({
  data = [],
  title = 'Table Viewer',
  className,
  variant = 'default', // default, card
  showTitle = true,
  striped = true, // AG Grid doesn't handle stripes natively, will add class if needed
  dense = false,
  hoverable = true,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  // Handle empty data
  if (!data || data.length === 0) {
    return (
      <Card className={cn('tableviewer-card', className)}>
        <CardContent className="tableviewer-card-content">
          <p className="tableviewer-no-data-text">No data available</p>
        </CardContent>
      </Card>
    );
  }

  // Define column definitions dynamically from data keys
  const columnDefs = useMemo(() => {
    if (data.length === 0) return [];
    return Object.keys(data[0]).map((key) => ({
      headerName: key,
      field: key,
      sortable: true,
      filter: true,
      resizable: true,
    }));
  }, [data]);

  // Grid Options
  const gridOptions = {
    rowHeight: dense ? 30 : 50,
    rowClass: hoverable ? 'ag-row-hover' : '',
    animateRows: true,
  };

  // Ag Grid Theme
  const gridTheme = 'ag-theme-alpine';

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
        style={{
          height: isExpanded ? '400px' : '0px',
          overflow: 'hidden',
          transition: 'height 0.3s',
        }}
      >
        {/* AG Grid Component */}
        <div className={gridTheme} style={{ width: '100%', height: '100%' }}>
          <AgGridReact
            rowData={data}
            columnDefs={columnDefs}
            gridOptions={gridOptions}
            domLayout="autoHeight"
          />
        </div>
      </div>
    </div>
  );

  // Card variant handling
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
