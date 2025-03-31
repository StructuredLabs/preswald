import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
import { ModuleRegistry } from '@ag-grid-community/core';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { AgGridReact } from 'ag-grid-react';

import React, { useEffect, useRef, useState } from 'react';

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const TableViewerWidget = ({
  rowData = [],
  title = 'Table Viewer',
  variant = 'default',
  showTitle = true,
  striped = true,
  dense = false,
  hoverable = true,
  className = '',
  pagination = true,
  paginationPageSize = 20,
  props: { rowData: propsRowData = [], columnDefs: propsColumnDefs = [], title: propsTitle } = {},
  ...commonProps
}) => {
  console.log('Received props:', { rowData, propsRowData, propsColumnDefs, title, propsTitle });

  const [isExpanded, setIsExpanded] = useState(true);
  const gridRef = useRef(null); // Reference for grid API

  // Convert columnDefs to use '/' instead of '.' and add valueFormatter
  const transformedColumnDefs = propsColumnDefs.map((col) => ({
    ...col,
    field: col.field.replace(/\./g, '/'),
    valueFormatter: (params) =>
      params.value === '' || params.value === null ? 'null' : params.value,
    sortable: true, // Enable sorting
    filter: true, // Enable filtering
    resizable: true, // Enable column resizing
  }));

  // Convert grid data keys to use '/' instead of '.' and replace empty strings with null
  const transformGridData = (data) => {
    return data.map((row) => {
      const newRow = {};
      for (const key in row) {
        if (row.hasOwnProperty(key)) {
          const newKey = key.replace(/\./g, '/');
          const value = row[key] === '' ? null : String(row[key]);
          newRow[newKey] = value;
        }
      }
      return newRow;
    });
  };

  const [gridData, setGridData] = useState(
    transformGridData(propsRowData.length ? propsRowData : rowData)
  );
  const [columnDefs, setColumnDefs] = useState(transformedColumnDefs);

  useEffect(() => {
    setGridData(transformGridData(propsRowData.length ? propsRowData : rowData));
    setColumnDefs(transformedColumnDefs);
  }, [propsRowData, rowData, propsColumnDefs]);

  const displayTitle = propsTitle !== undefined ? propsTitle : title;

  // Export data to CSV (AG Grid Community supports this)
  const exportToCSV = () => {
    gridRef.current.api.exportDataAsCsv();
  };

  return (
    <div
      style={{
        width: '100%',
        margin: '1rem 0',
        borderRadius: '8px',
        overflow: 'hidden',
        border: variant === 'card' ? '1px solid #e0e0e0' : 'none',
        boxShadow: variant === 'card' ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
      }}
      className={`ag-theme-alpine ${className}`}
    >
      {showTitle && (
        <div
          style={{
            padding: '1rem',
            backgroundColor: '#f8f9fa',
            borderBottom: '1px solid #e0e0e0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <h3 style={{ margin: 0, fontSize: '1.25rem' }}>{displayTitle}</h3>
          <div>
            <button onClick={exportToCSV} style={{ marginRight: '10px' }}>
              Export CSV
            </button>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '1.2rem',
            }}
          >
            {isExpanded ? '🔼' : '🔽'}
          </button>
        </div>
      )}

      <div
        style={{
          height: isExpanded ? '500px' : '0',
          transition: 'height 0.3s ease-in-out',
          overflow: 'hidden',
        }}
      >
        {gridData.length > 0 && columnDefs.length > 0 ? (
          <AgGridReact
            ref={gridRef}
            columnDefs={columnDefs}
            rowData={gridData}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
              flex: 1,
            }}
            rowSelection="multiple" // Enable row selection
            pagination={pagination}
            paginationPageSize={paginationPageSize}
            suppressRowHoverHighlight={!hoverable}
            getRowStyle={(params) => ({
              backgroundColor: striped && params.node.rowIndex % 2 === 0 ? '#f8f9fa' : 'white',
            })}
            rowHeight={dense ? 40 : 50}
            animateRows={true} // Enable smooth animations
            enableRangeSelection={true} // Allow cell range selection
            enableSorting={true} // Enable sorting
            enableFilter={true} // Enable filtering
            suppressMovableColumns={false} // Allow column reordering
            enableCellTextSelection={true} // Allow text selection in cells
            onGridReady={(params) => params.api.sizeColumnsToFit()}
            onFirstDataRendered={(params) => params.api.sizeColumnsToFit()}
            {...commonProps}
          />
        ) : (
          <div
            style={{
              padding: '2rem',
              textAlign: 'center',
              color: '#6c757d',
              backgroundColor: '#f8f9fa',
            }}
          >
            No data available to display
          </div>
        )}
      </div>
    </div>
  );
};

export default TableViewerWidget;
