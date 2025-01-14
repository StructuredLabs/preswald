import React, { useEffect, useState } from 'react';

import { websocket } from '../../utils/websocket';

function ConnectionCard({ connection }) {
  const handleOnClickConnectionCard = async (e) => {
    e.stopPropagation();
    e.preventDefault();
    // Handle view modal
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
    <div
      className="p-4 border rounded-lg flex items-center justify-between mb-2 cursor-pointer hover:bg-gray-50"
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