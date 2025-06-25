import { ArrowDown, ArrowUp, AlertTriangle } from 'lucide-react';
import React from 'react';

import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

const formatNumber = (num) => {
  if (Math.abs(num) >= 1e9) return (num / 1e9).toFixed(1) + 'B';
  if (Math.abs(num) >= 1e6) return (num / 1e6).toFixed(1) + 'M';
  if (Math.abs(num) >= 1e3) return (num / 1e3).toFixed(1) + 'K';
  return num;
};

const BigNumberCard = ({ id, label, value, delta, unit, error, className }) => {
  const deltaNumber = parseFloat(delta);
  const isPositive = deltaNumber >= 0;

  console.log(`BigNumberCard ${id} ${label}`, {value, error})
  const displayDelta =
    typeof delta === 'string' ? delta : `${isPositive ? '+' : ''}${delta}${unit ?? ''}`;

  return (
    <div
      id={id}
      className={cn(
        'bg-white rounded-xl shadow p-4 w-full max-w-xs relative',
        error && 'border-destructive border-2 bg-red-50',
        className
      )}
    >
      {error && (
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="absolute top-2 right-2 text-destructive">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <span>{error.toString()}</span>
          </TooltipContent>
        </Tooltip>
      )}

      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-3xl font-bold text-gray-800 break-words leading-tight max-w-full">
        {error
          ? <span className="text-gray-400 italic">unavailable</span>
          : Number.isFinite(value)
            ? `${formatNumber(value)}${unit ?? ''}`
            : String(value)}
      </div>
      {delta !== undefined && (
        <div
          className={cn(
            'flex items-center mt-1 text-sm',
            isPositive ? 'text-green-600' : 'text-red-600'
          )}
        >
          {isPositive ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
          <span className="ml-1">{displayDelta}</span>
        </div>
      )}
    </div>
  );
};

export default BigNumberCard;
