import { ArrowDownRight, ArrowUpRight, User } from 'lucide-react';
import * as LucideIcons from 'lucide-react';

import React from 'react';

const formatNumber = (value) => {
  if (typeof value === 'string' && /[KMBT]$/.test(value.trim())) {
    // Already formatted string (like 12.5M), return as-is
    return value;
  }

  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return value;
  if (num >= 1e12) return (num / 1e12).toFixed(1) + 'T';
  if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
  return num.toString();
};

const BigNumberCard = ({
  value,
  label,
  delta,
  deltaColor = 'green',
  icon = 'User',
  description = '',
}) => {
  const formattedValue = formatNumber(value);
  const IconComponent = icon && LucideIcons[icon] ? LucideIcons[icon] : User;

  const deltaClass = deltaColor ? `text-${deltaColor}-600` : 'text-green-600';

  return (
    <div className="bg-white rounded-3xl p-8 w-80 max-w-sm bignumber transition-shadow duration-300 border border-gray-100 shadow-md hover:shadow-lg">
      <div className="flex flex-col gap-2">
        {/* Top: Delta */}
        <div className="flex justify-end">
          {delta && (
            <div className={`flex items-center gap-1 ${deltaClass} -mr-4 pl-4`}>
              {parseFloat(delta) >= 0 ? <ArrowUpRight size={20} /> : <ArrowDownRight size={20} />}
              <span className="text-sm font-medium">{delta.toString().replace('.', '.')}</span>
            </div>
          )}
        </div>

        {/* Label */}
        <p className="text-base text-gray-600 text-lg -mt-8 -ml-4">{label}</p>

        {/* Big Number + Icon */}
        <div className="flex items-center justify-between mt-2">
          <h2 className="text-4xl font-bold tracking-tight">{formattedValue}</h2>
          <IconComponent className="text-gray-500 mr-7" size={40} />
        </div>
        {/* Description */}
        {description?.trim() && <p className="text-base text-gray-500 mt-5 -ml-3">{description}</p>}
      </div>
    </div>
  );
};

export default BigNumberCard;
