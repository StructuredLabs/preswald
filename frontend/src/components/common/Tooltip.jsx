import React, { useState } from 'react';

export const Tooltip = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      {isVisible && (
        <div
          className="absolute z-50 px-2 py-1 text-xs font-medium text-white bg-gray-900 rounded-md whitespace-nowrap transition-all duration-200"
          style={{
            top: '100%',
            left: '50%',
            transform: `translateX(-50%) translateY(${isVisible ? '0' : '5px'})`,
            marginTop: '0.5rem',
            opacity: isVisible ? 1 : 0,
          }}
        >
          {content}
          <div
            className="absolute w-0 h-0"
            style={{
              top: '-4px',
              left: '50%',
              transform: 'translateX(-50%)',
              borderLeft: '4px solid transparent',
              borderRight: '4px solid transparent',
              borderBottom: '4px solid #111827',
            }}
          />
        </div>
      )}
    </div>
  );
}; 