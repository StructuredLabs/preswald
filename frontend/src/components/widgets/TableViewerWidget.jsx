import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
import { ModuleRegistry } from '@ag-grid-community/core';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { AgGridReact } from 'ag-grid-react';

import React, { useEffect, useState } from 'react';

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
  paginationPageSize = 10,
  props: { rowData: propsRowData = [], columnDefs: propsColumnDefs = [], title: propsTitle } = {},
  ...commonProps
}) => {
  console.log('Received props:', {
    rowData,
    propsRowData,
    propsColumnDefs,
    title,
    propsTitle,
  });

  const [isExpanded, setIsExpanded] = useState(true);
  const [gridData, setGridData] = useState(propsRowData.length ? propsRowData : rowData);
  const [columnDefs, setColumnDefs] = useState(propsColumnDefs);

  useEffect(() => {
    // Function to convert data to strings
    const convertDataToStrings = (data) => {
      return data.map((row) => {
        const newRow = {};
        for (const key in row) {
          if (row.hasOwnProperty(key)) {
            newRow[key] = String(row[key]); // Convert each value to a string
          }
        }
        return newRow;
      });
    };

    // Apply the conversion
    const stringData = convertDataToStrings(gridData);
    setGridData(stringData); // Set the converted data back to gridData

    // Debug: Check the structure and content of stringData
    console.log('stringData:', stringData);

    // Generate column definitions if not provided
    if (!propsColumnDefs.length && stringData.length) {
      const generatedColumnDefs = Object.keys(stringData[0]).map((key) => ({
        headerName: key,
        field: key,
        sortable: true,
        filter: true,
        resizable: true,
        flex: 1,
        cellStyle: {
          paddingTop: dense ? '4px' : '8px',
          paddingBottom: dense ? '4px' : '8px',
        },
        valueFormatter: (params) => params.value, // Simple valueFormatter
      }));

      setColumnDefs(generatedColumnDefs);

      // Debug: Check the generated column definitions
      console.log('generatedColumnDefs:', generatedColumnDefs);
    }
  }, [gridData, dense, propsColumnDefs]);

  const displayTitle = propsTitle !== undefined ? propsTitle : title;

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
            columnDefs={columnDefs}
            rowData={gridData}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
              flex: 1,
            }}
            pagination={pagination}
            paginationPageSize={paginationPageSize}
            suppressRowHoverHighlight={!hoverable}
            getRowStyle={(params) => ({
              backgroundColor: striped && params.node.rowIndex % 2 === 0 ? '#f8f9fa' : 'white',
            })}
            rowHeight={dense ? 40 : 50}
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
