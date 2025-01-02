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
  console.log({connection});
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
        {/* <Menu as="div" className="relative inline-block text-left">
          <Menu.Button
            className="flex items-center text-gray-500 hover:text-gray-700 focus:outline-none"
            onClick={handleMenuClick}
          >
            <HiDotsVertical className="w-5 h-5" />
          </Menu.Button>
          <Menu.Items className="z-10 absolute right-0 mt-2 w-40 origin-top-right bg-white border border-gray-200 divide-y divide-gray-100 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
            <div className="py-1 bg-white">
              <Menu.Item>
                {({ active }) => (
                  <button
                    className={`${active ? 'bg-gray-100' : ''} group flex items-center w-full px-4 py-2 text-sm text-gray-700`}
                    onClick={(e) => {
                      e.stopPropagation();
                      // Handle view
                    }}
                  >
                    <MdOutlineViewList className="w-4 h-4 mr-2 text-gray-700 text-sm font-bold" />
                    View
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button
                    className={`${active ? 'bg-gray-100' : ''} group flex items-center w-full px-4 py-2 text-sm text-gray-700`}
                    onClick={(e) => {
                      e.stopPropagation();
                      // Handle refresh
                    }}
                  >
                    <FiRefreshCw className="w-3 h-3 mr-2 text-gray-800 text-sm font-extrabold" />
                    Refresh
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button
                    className={`${active ? 'bg-gray-100' : ''} group flex items-center w-full px-4 py-2 text-sm text-gray-700`}
                    onClick={(e) => {
                      e.stopPropagation();
                      // Handle delete
                    }}
                  >
                    <FaRegTrashAlt className="w-3 h-3 mr-2 text-gray-700 text-sm" />
                    Delete
                  </button>
                )}
              </Menu.Item>
            </div>
          </Menu.Items>
        </Menu> */}
      </div>
    </div>
  );
}

const Connections = () => {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleWebSocketMessage = (message) => {
      if (message.type === 'connections_update') {
        setConnections(message.connections);
        setLoading(false);
      }
    };

    const unsubscribe = websocket.subscribe(handleWebSocketMessage);
    return () => unsubscribe();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col py-5 px-10 w-full">
      <div className="text-left w-full">
        {connections.length === 0 ? (
          <div className="mt-20 flex flex-col w-full h-full items-center justify-center">
            <p>No connections available</p>
          </div>
        ) : (
          connections.map((connection, index) => (
            <ConnectionCard key={index} connection={connection} />
          ))
        )}
      </div>
    </div>
  );
};

export default Connections;