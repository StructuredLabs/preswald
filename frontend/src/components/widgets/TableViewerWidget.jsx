import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
import { ModuleRegistry } from '@ag-grid-community/core';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { AgGridReact } from 'ag-grid-react';

import React from 'react';

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
  const columns = propsColumnDefs.map((col) => ({
    ...col,
    field: col.field.replace(/\./g, '/'),
    valueFormatter: (params) => params.value ?? 'null',
    sortable: true,
    filter: true,
    resizable: true,
  }));

  const data = (propsRowData.length ? propsRowData : rowData).map((row) => {
    const newRow = {};
    Object.entries(row).forEach(([key, value]) => {
      newRow[key.replace(/\./g, '/')] = value ?? null;
    });
    return newRow;
  });

  return (
    <div
      className={`w-full rounded-sm overflow-hidden ${
        hasCard ? 'border border-gray-50 shadow-sm bg-white' : ''
      } ag-theme-alpine ${className} [&_.ag-row-alt]:bg-white`}
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
            }}
            pagination={pagination}
            paginationPageSize={paginationPageSize}
            getRowStyle={() => ({
              backgroundColor: 'white',
            })}
            rowHeight={36}
            headerHeight={28}
            onGridReady={(params) => params.api.sizeColumnsToFit()}
            {...commonProps}
          />
        ) : (
          <div className="p-10 text-center text-gray-500 bg-gray-50 text-sm">
            No data available to display
          </div>
        )}
      </div>
    </div>
  );
};

export default TableViewerWidget;
