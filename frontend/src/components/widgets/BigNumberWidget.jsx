import { ArrowDown, ArrowUp } from 'lucide-react';

import React from 'react';

// Utility to format large numbers
const formatNumber = (num) => {
  if (Math.abs(num) >= 1e9) return (num / 1e9).toFixed(1) + 'B';
  if (Math.abs(num) >= 1e6) return (num / 1e6).toFixed(1) + 'M';
  if (Math.abs(num) >= 1e3) return (num / 1e3).toFixed(1) + 'K';
  return num;
};

const BigNumberCard = ({ label, value, delta, unit }) => {
  const deltaNumber = parseFloat(delta);
  const isPositive = deltaNumber >= 0;

  const displayDelta =
    typeof delta === 'string' ? delta : `${isPositive ? '+' : ''}${delta}${unit ?? ''}`;

  return (
    <div className="bg-white rounded-xl shadow p-4 w-full max-w-xs">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-3xl font-bold text-gray-800">
        {formatNumber(value)}
        {unit ?? ''}
      </div>
      {delta !== undefined && (
        <div
          className={`flex items-center mt-1 text-sm ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {isPositive ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
          <span className="ml-1">{displayDelta}</span>
        </div>
      )}
    </div>
  );
};

export default BigNumberCard;
