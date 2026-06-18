import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
import { ModuleRegistry } from '@ag-grid-community/core';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import 'ag-grid-community/styles/ag-theme-alpine-dark.css';
import { AgGridReact } from 'ag-grid-react';

import React, { useEffect, useState, useCallback, useMemo } from 'react';

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const TableViewerWidget = ({
  rowData = [],
  hasCard = false,
  className = '',
  pagination = true,
  paginationPageSize = 20,
  props: { rowData: propsRowData = [], columnDefs: propsColumnDefs = [] } = {},
  ...commonProps
}) => {
  const [isDark, setIsDark] = useState(false);

  // Enhanced dark theme detection with multiple fallbacks
  const checkDarkTheme = useCallback(() => {
    // Check multiple sources for dark theme
    const darkSources = [
      document.documentElement.classList.contains('dark'),
      document.body.classList.contains('dark'),
      document.documentElement.getAttribute('data-theme') === 'dark',
      window.matchMedia?.('(prefers-color-scheme: dark)').matches,
      // Check CSS custom properties
      getComputedStyle(document.documentElement).getPropertyValue('--background')?.includes('dark')
    ];
    
    const isDarkMode = darkSources.some(Boolean);
    setIsDark(isDarkMode);
    
    // Debug logging for development
    if (process.env.NODE_ENV === 'development') {
      console.log('Dark theme sources:', {
        documentElement: darkSources[0],
        body: darkSources[1],
        dataTheme: darkSources[2],
        mediaQuery: darkSources[3],
        cssProps: darkSources[4],
        final: isDarkMode
      });
    }
  }, []);

  // Enhanced theme monitoring with multiple observers
  useEffect(() => {
    checkDarkTheme();

    // Monitor document element class changes
    const docObserver = new MutationObserver(checkDarkTheme);
    docObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class', 'data-theme', 'style']
    });

    // Monitor body class changes (some apps use body for theming)
    const bodyObserver = new MutationObserver(checkDarkTheme);
    bodyObserver.observe(document.body, {
      attributes: true,
      attributeFilter: ['class', 'data-theme']
    });

    // Monitor system theme preference changes
    const mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)');
    const handleMediaChange = () => checkDarkTheme();
    mediaQuery?.addEventListener?.('change', handleMediaChange);

    return () => {
      docObserver.disconnect();
      bodyObserver.disconnect();
      mediaQuery?.removeEventListener?.('change', handleMediaChange);
    };
  }, [checkDarkTheme]);

  // Memoized column definitions with enhanced dark theme styling
  const columns = useMemo(() => 
    propsColumnDefs.map((col) => ({
      ...col,
      field: col.field.replace(/\./g, '/'),
      valueFormatter: (params) => params.value ?? 'null',
      sortable: true,
      filter: true,
      resizable: true,
      // Enhanced cell styling for dark theme
      cellStyle: (params) => {
        const baseStyle = {
          borderRight: isDark ? '1px solid hsl(var(--border))' : '1px solid #e5e7eb',
          color: isDark ? 'hsl(var(--foreground))' : '#374151',
        };
        
        // Add custom styling if provided in column definition
        return col.cellStyle ? { ...baseStyle, ...col.cellStyle(params) } : baseStyle;
      },
      // Enhanced header styling
      headerCellStyle: {
        backgroundColor: isDark ? 'hsl(var(--muted))' : '#f9fafb',
        color: isDark ? 'hsl(var(--foreground))' : '#374151',
        borderBottom: isDark ? '2px solid hsl(var(--border))' : '2px solid #e5e7eb',
        fontWeight: '600',
      }
    })), 
    [propsColumnDefs, isDark]
  );

  // Memoized row data processing
  const data = useMemo(() => 
    (propsRowData.length ? propsRowData : rowData).map((row) => {
      const newRow = {};
      Object.entries(row).forEach(([key, value]) => {
        newRow[key.replace(/\./g, '/')] = value ?? null;
      });
      return newRow;
    }), 
    [propsRowData, rowData]
  );

  // Enhanced theme and styling logic
  const gridTheme = isDark ? 'ag-theme-alpine-dark' : 'ag-theme-alpine';
  
  const cardClasses = hasCard 
    ? `border shadow-sm rounded-lg ${
        isDark 
          ? 'border-border bg-card text-card-foreground' 
          : 'border-gray-200 bg-white text-gray-900'
      }` 
    : '';
  
  // Enhanced alternating row styling
  const altRowClass = isDark 
    ? '[&_.ag-row-alt]:bg-muted/30 [&_.ag-row-even]:bg-background [&_.ag-row-odd]:bg-muted/15' 
    : '[&_.ag-row-alt]:bg-gray-50 [&_.ag-row-even]:bg-white [&_.ag-row-odd]:bg-gray-25';

  // Enhanced no-data styling
  const noDataClasses = `p-10 text-center text-sm rounded-md ${
    isDark 
      ? 'text-muted-foreground bg-muted/50 border border-border' 
      : 'text-gray-500 bg-gray-50 border border-gray-200'
  }`;

  // Enhanced grid styling with CSS custom properties support
  const getRowStyle = useCallback((params) => {
    const isEven = params.node.rowIndex % 2 === 0;
    
    if (isDark) {
      return {
        backgroundColor: isEven 
          ? 'hsl(var(--background))' 
          : 'hsl(var(--muted) / 0.3)',
        color: 'hsl(var(--foreground))',
        borderBottom: '1px solid hsl(var(--border))',
      };
    } else {
      return {
        backgroundColor: isEven ? 'white' : '#fafafa',
        color: '#374151',
        borderBottom: '1px solid #e5e7eb',
      };
    }
  }, [isDark]);

  return (
    <div
      className={`w-full rounded-sm overflow-hidden ${cardClasses} ${gridTheme} ${className} ${altRowClass}`}
      style={{
        // CSS custom properties for consistent theming
        '--ag-background-color': isDark ? 'hsl(var(--background))' : 'white',
        '--ag-foreground-color': isDark ? 'hsl(var(--foreground))' : '#374151',
        '--ag-border-color': isDark ? 'hsl(var(--border))' : '#e5e7eb',
        '--ag-header-background-color': isDark ? 'hsl(var(--muted))' : '#f9fafb',
        '--ag-odd-row-background-color': isDark ? 'hsl(var(--muted) / 0.15)' : '#fafafa',
        '--ag-even-row-background-color': isDark ? 'hsl(var(--background))' : 'white',
      }}
    >
      <div id={commonProps.id} className="h-[500px]">
        {data.length > 0 && columns.length > 0 ? (
          <AgGridReact
            columnDefs={columns}
            rowData={data}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
              flex: 1,
              minWidth: 100,
              // Enhanced filter styling for dark theme
              filterParams: {
                filterOptions: ['contains', 'equals', 'startsWith', 'endsWith'],
                suppressAndOrCondition: false,
              }
            }}
            pagination={pagination}
            paginationPageSize={paginationPageSize}
            getRowStyle={getRowStyle}
            rowHeight={36}
            headerHeight={32}
            onGridReady={(params) => {
              params.api.sizeColumnsToFit();
              // Ensure theme is applied after grid is ready
              setTimeout(() => checkDarkTheme(), 100);
            }}
            // Enhanced theme-aware grid options
            gridOptions={{
              suppressCellFocus: false,
              enableRangeSelection: true,
              suppressRowClickSelection: false,
              // Dark theme aware popup styling
              popupParent: document.body,
            }}
            {...commonProps}
          />
        ) : (
          <div className={noDataClasses}>
            <div className="mb-2">
              <svg 
                className={`mx-auto h-12 w-12 ${isDark ? 'text-muted-foreground' : 'text-gray-400'}`}
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={1} 
                  d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2h2a2 2 0 002-2z" 
                />
              </svg>
            </div>
            <h3 className={`text-sm font-medium ${isDark ? 'text-foreground' : 'text-gray-900'}`}>
              No data available
            </h3>
            <p className={`mt-1 text-xs ${isDark ? 'text-muted-foreground' : 'text-gray-500'}`}>
              Upload a dataset or check your data source configuration
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TableViewerWidget;