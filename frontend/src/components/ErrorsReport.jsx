import React from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';

const ErrorsReport = ({ errors }) => {
  if (!errors || errors.length === 0) return null;

  return (
    <Alert variant="destructive" className="dashboard-error space-y-2">
      <AlertTitle>Errors detected during source transformation</AlertTitle>
      <AlertDescription>
        <ul className="list-disc list-inside space-y-1">
          {errors.map((err, idx) => (
            <li key={idx}>
              <strong>{err.filename}:{err.lineno}</strong> — {err.message}
            </li>
          ))}
        </ul>
      </AlertDescription>
    </Alert>
  );
};

export { ErrorsReport as default,  ErrorsReport };
