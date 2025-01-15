import React, { useEffect, useState } from 'react';

import { websocket } from '../../utils/websocket';

function MetadataView({ metadata, type }) {
  if (!metadata || metadata.error) {
    return (
      <div className="text-sm text-red-500">
        {metadata?.error || 'No metadata available'}
      </div>
    );
  }

  switch (type.toLowerCase()) {
    case 'postgresql':
      return (
        <div className="space-y-2">
          <div className="text-sm">
            <span className="font-medium">Database:</span> {metadata.database_name}
          </div>
          <div className="text-sm">
            <span className="font-medium">Total Tables:</span> {metadata.total_tables}
          </div>
          <div className="mt-2">
            <div className="font-medium text-sm mb-1">Schemas:</div>
            {Object.entries(metadata.schemas).map(([schema, tables]) => (
              <div key={schema} className="ml-2">
                <div className="text-sm font-medium text-gray-600">{schema}</div>
                <div className="ml-2">
                  {Object.entries(tables).map(([table, info]) => (
                    <details key={table} className="mb-1">
                      <summary className="text-sm text-blue-600 cursor-pointer">
                        {table} ({info.columns.length} columns)
                      </summary>
                      <div className="ml-4 mt-1">
                        {info.columns.map((col) => (
                          <div key={col.name} className="text-sm">
                            <span className="text-gray-600">{col.name}</span>
                            <span className="text-gray-400 ml-1">({col.type})</span>
                          </div>
                        ))}
                      </div>
                    </details>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      );

    case 'csv':
      return (
        <div className="space-y-2">
          <div className="text-sm">
            <span className="font-medium">File Size:</span> {metadata.file_size}
          </div>
          <div className="text-sm">
            <span className="font-medium">Total Rows:</span> {metadata.total_rows}
          </div>
          <div className="text-sm">
            <span className="font-medium">Total Columns:</span> {metadata.total_columns}
          </div>
          <div className="mt-2">
            <div className="font-medium text-sm mb-1">Columns:</div>
            <div className="grid grid-cols-1 gap-2">
              {metadata.columns.map((col) => (
                <details key={col.name} className="text-sm">
                  <summary className="cursor-pointer text-blue-600">
                    {col.name} ({col.type})
                  </summary>
                  <div className="ml-4 mt-1">
                    <div className="text-gray-600">Sample Values:</div>
                    <div className="text-gray-500">
                      {col.sample_values.map((val, i) => (
                        <div key={i}>{String(val)}</div>
                      ))}
                    </div>
                  </div>
                </details>
              ))}
            </div>
          </div>
        </div>
      );

    default:
      return (
        <div className="text-sm text-gray-500">
          No metadata display configured for this connection type
        </div>
      );
  }
}

function ConnectionCard({ connection }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleOnClickConnectionCard = async (e) => {
    e.stopPropagation();
    e.preventDefault();
    setIsExpanded(!isExpanded);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'configured':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConnectionIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'postgresql':
        return '🐘';
      case 'mysql':
        return '🐬';
      case 'csv':
        return '📄';
      case 'parquet':
        return '📦';
      case 'json':
        return '🔗';
      default:
        return '🔌';
    }
  };

  return (
    <div className="border rounded-lg overflow-hidden">
      <div
        className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50"
        onClick={handleOnClickConnectionCard}
      >
        <div className="flex items-center">
          <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mr-4">
            <span className="text-lg" role="img" aria-label={connection.type}>
              {getConnectionIcon(connection.type)}
            </span>
          </div>
          <div>
            <div className="flex items-center">
              <p className="text-sm font-semibold text-gray-700 mr-2">
                {connection.name}
              </p>
              <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full capitalize ${getStatusColor(connection.status)}`}>
                {connection.status}
              </span>
            </div>
            <div className="mt-1">
              <p className="text-sm text-gray-500">
                Type: {connection.type}
              </p>
              <p className="text-sm text-gray-500">
                {connection.details}
              </p>
            </div>
          </div>
        </div>
        <div className="text-gray-400">
          <svg
            className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>
      {isExpanded && (
        <div className="px-4 py-3 bg-gray-50 border-t">
          <div className="text-sm font-medium text-gray-700 mb-2">Metadata</div>
          <MetadataView metadata={connection.metadata} type={connection.type} />
        </div>
      )}
    </div>
  );
}

function Connections() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConnections = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/connections');
        if (!response.ok) {
          throw new Error('Failed to fetch connections');
        }
        const data = await response.json();
        setConnections(data.connections || []);
      } catch (error) {
        console.error('Error fetching connections:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchConnections();

    const unsubscribe = websocket.subscribe((message) => {
      if (message.type === 'connections_update') {
        setConnections(message.connections || []);
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  if (loading) {
    return (
      <div className="p-4">
        <div className="text-center text-gray-500 py-8">
          Loading connections...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center text-red-500 py-8">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Connections</h1>
      <div className="space-y-4">
        {connections.map((connection, index) => (
          <ConnectionCard key={`${connection.name}-${index}`} connection={connection} />
        ))}
        {connections.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            No connections found. Add connections in your config.toml file to get started.
          </div>
        )}
      </div>
    </div>
  );
}

export default Connections;