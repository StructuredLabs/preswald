import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { AgGridReact } from 'ag-grid-react';

import React, { useEffect, useState } from 'react';

function TableViewerWidget({ columnDefs, rowData }) {
  const [gridColumnDefs, setGridColumnDefs] = useState([]);
  const [gridRowData, setGridRowData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('Received Backend Data:', { columnDefs, rowData });

    if (columnDefs && rowData) {
      setGridColumnDefs(columnDefs);
      setGridRowData(rowData);
      setLoading(false);
    }
  }, [columnDefs, rowData]);

  return (
    <div className="ag-theme-alpine" style={{ height: '500px', width: '100%' }}>
      {loading ? (
        <p>Loading data...</p>
      ) : gridColumnDefs.length === 0 || gridRowData.length === 0 ? (
        <p>No data available to display.</p>
      ) : (
        <AgGridReact
          columnDefs={gridColumnDefs}
          rowData={gridRowData}
          defaultColDef={{ resizable: true, sortable: true, filter: true }}
          pagination={true}
          paginationPageSize={10}
        />
      )}
    </div>
  );
}

export default TableViewerWidget;
