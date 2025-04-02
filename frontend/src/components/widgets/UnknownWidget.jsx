import { ExclamationTriangleIcon } from '@radix-ui/react-icons';

import React from 'react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

import { cn } from '@/lib/utils';

const UnknownWidget = ({
  type = 'unknown',
  id,
  className,
  variant = 'default', // default, destructive
}) => {
  return (
    <Alert
      variant={variant === 'default' ? 'default' : 'destructive'}
      className={cn('unknownwidget-container', className)}
    >
      <ExclamationTriangleIcon className="unknownwidget-icon" />
      <AlertTitle>Unknown Widget Type</AlertTitle>
      <AlertDescription className="unknownwidget-description">
        <div className="unknownwidget-text">
          <p>
            The widget type <code className="unknownwidget-code">{type}</code> is not recognized.
          </p>
          {id && (
            <p className="unknownwidget-muted-text">
              Widget ID: <code className="font-mono">{id}</code>
            </p>
          )}
          <p className="unknownwidget-muted-text">
            Please check the widget type and ensure it is correctly specified.
          </p>
        </div>
      </AlertDescription>
    </Alert>
  );
};

export default UnknownWidget;
