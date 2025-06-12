import React from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';

import { ErrorsReport } from '../ErrorsReport'
import DynamicComponents from '../DynamicComponents';
import LoadingState from '../LoadingState';

const Dashboard = ({ components, error, transformErrors, handleComponentUpdate }) => {
  console.log('[Dashboard] Rendering with:', { components, error, transformErrors });

  const isValidComponents =
    components &&
    components.rows &&
    Array.isArray(components.rows) &&
    components.rows.every((row) => Array.isArray(row));

  const renderContent = () => {
    const showTransformErrorBanner = transformErrors && transformErrors.length > 0;

    const errorFragment = showTransformErrorBanner ? (
      <div className="dashboard-error-fragment">
        <ErrorsReport errors={transformErrors} />
      </div>
    ) : null;

    const emptyWrapperClass = showTransformErrorBanner
      ? 'dashboard-empty-with-errors' : 'dashboard-empty';

    if (error || !isValidComponents) {
      const alertMessage = error ?? 'Invalid components data'
        return (
          <div className={`${emptyWrapperClass}`}>
            <Alert variant="destructive" className="dashboard-error">
              <AlertDescription>{alertMessage}</AlertDescription>
            </Alert>

            {errorFragment}
          </div>
        )
    }

    if (components.rows.length === 0) {
      return (
        <div className={`${emptyWrapperClass}`}>
          {errorFragment}
          <p className="dashboard-empty-text">No components to display</p>
        </div>
      )
    }

    return (
      <>
        {errorFragment}
        <DynamicComponents components={components} onComponentUpdate={handleComponentUpdate} />
      </>
    )
  };

  return <div className="dashboard-container">{renderContent()}</div>;
};

export default Dashboard;
