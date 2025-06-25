import React from 'react';
import { AlertTriangle } from 'lucide-react';

import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

const GenericWidget = ({ id, value, mimetype = 'text/plain', error, className }) => {
  const cleanMime = mimetype.split(';')[0].trim().toLowerCase();
  const renderContent = () => {
    if (!value) {
      return <div className="text-gray-500 italic">No content to display.</div>;
    }

    if (cleanMime.startsWith('image/')) {
      return (
        <img
          src={value}
          alt="rendered image"
          className="rounded-lg shadow max-w-full mx-auto"
        />
      );
    }

    if (cleanMime === 'text/html') {
      return (
        <div
          className="prose max-w-none"
          dangerouslySetInnerHTML={{ __html: value }}
        />
      );
    }

    if (cleanMime === 'application/pdf') {
      return (
        <iframe
          src={value}
          title="PDF viewer"
          className="w-full h-[600px] border rounded"
        />
      );
    }

    if ([
      'text/plain',
      'application/json',
      'text/csv',
      'text/markdown'
    ].includes(cleanMime)) {
      return (
        <pre className="text-sm text-gray-800 whitespace-pre-wrap p-2 bg-gray-100 rounded">
          {value}
        </pre>
      );
    }

    return (
      <div className="text-sm text-gray-500 italic">
        Unsupported mimetype <code>{mimetype}</code>
      </div>
    );
  };

  return (
    <div
      id={id}
      className={cn(
        'relative border rounded-md shadow-sm p-4 bg-white overflow-x-auto',
        error ? 'border-destructive border-2 bg-red-50' : 'border-gray-200',
        className
      )}
    >
      {error && (
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="absolute top-2 right-2 text-destructive z-10">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <span>{error.toString()}</span>
          </TooltipContent>
        </Tooltip>
      )}
      {renderContent()}
    </div>
  );
};

export default GenericWidget;
