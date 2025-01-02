import React, { useEffect, useState } from 'react';

import { FaRegTrashAlt } from 'react-icons/fa';
import { FiRefreshCw } from 'react-icons/fi';
import { HiDotsVertical } from 'react-icons/hi';
import { MdOutlineViewList } from 'react-icons/md';
import { Menu } from '@headlessui/react';
import { websocket } from '../../utils/websocket';

function formatDate(dateString) {
  const months = [
    'January',
    'February', 
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];

  const date = new Date(dateString);
  const month = months[date.getMonth()];
  const day = date.getDate();
  const year = date.getFullYear();

  return `${month} ${day}, ${year}`;
}

function ConnectionCard({ connection }) {
  const handleMenuClick = (event) => {
    event.stopPropagation();
  };

  const handleOnClickConnectionCard = async (e) => {
    e.stopPropagation();
    e.preventDefault();
    // Handle view modal
  };

  return (
    <div
      className="p-4 border rounded-lg flex items-center justify-between mb-2 cursor-pointer"
      onClick={handleOnClickConnectionCard}
    >
      <div className="flex items-center">
        <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center mr-4">
          <span className="text-lg font-semibold">
            {/* Icon placeholder */}
          </span>
        </div>
        <div className="flex flex-wrap items-center">
          <p className="text-sm font-semibold text-gray-700 mr-2">
            {connection.name}
          </p>
          <p className="text-sm text-gray-500 mr-2">
            • Details: {connection.details}
          </p>
          <p className="text-sm text-gray-500 mr-2">
            • {formatDate(new Date())}
          </p>
        </div>
      </div>
      <div className="flex items-center">
        <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-green-800 bg-green-100 rounded-full mr-4 capitalize">
          Active
        </span>
      </div>
    </div>
  );
}

function Connections() {
  const [connections, setConnections] = useState([]);

  useEffect(() => {
    // Initial fetch of connections
    fetch('/api/connections')
      .then(response => response.json())
      .then(data => {
        setConnections(data.connections || []);
      })
      .catch(error => console.error('Error fetching connections:', error));

    // Subscribe to websocket updates
    const unsubscribe = websocket.subscribe((message) => {
      if (message.type === 'connections_update') {
        // Replace all connections with the new list
        setConnections(message.connections || []);
      }
    });

    // Cleanup subscription
    return () => {
      unsubscribe();
    };
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Connections</h1>
      <div className="space-y-4">
        {connections.map((connection, index) => (
          <ConnectionCard key={`${connection.name}-${index}`} connection={connection} />
        ))}
        {connections.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            No active connections. Create a connection to get started.
          </div>
        )}
      </div>
    </div>
  );
}

export default Connections;