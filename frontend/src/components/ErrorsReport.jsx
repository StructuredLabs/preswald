import React, { useState, useRef, useEffect } from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';

const ErrorTypeBadge = ({ type }) => {
  const styles = {
    runtime: 'error-badge error-badge-runtime',
    ast_transform: 'error-badge error-badge-transform',
  };
  const labels = {
    runtime: 'Runtime',
    ast_transform: 'Transform',
  };

  return (
    <span className={styles[type] || 'error-badge'}>
      {labels[type] || type}
    </span>
  );
};

const ErrorsReport = ({ errors }) => {
  const [expanded, setExpanded] = useState(false);
  const [wasOverflowingWhenCollapsed, setWasOverflowingWhenCollapsed] = useState(false);
  const containerRef = useRef(null);
  const EXPAND_COLLAPSE_TRANSITION_MS = 300; // must match duration in .error-report-container

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    // Only measure overflow when not expanded
    if (!expanded) {
      const timeout = setTimeout(() => {
        const isOverflowing = el.scrollHeight > el.clientHeight;
        setWasOverflowingWhenCollapsed(isOverflowing);
      }, EXPAND_COLLAPSE_TRANSITION_MS);

      return () => clearTimeout(timeout);
    }
  }, [errors, expanded]);

  if (!errors || errors.length === 0) return null;

  const hasRuntime = errors.some(e => e.type === 'runtime');
  const hasTransform = errors.some(e => e.type === 'ast_transform');
  const title = hasRuntime && hasTransform
    ? `${errors.length} error${errors.length > 1 ? 's' : ''} detected`
    : hasRuntime
      ? `${errors.length} runtime error${errors.length > 1 ? 's' : ''}`
      : 'Errors detected during source transformation';

  return (
    <Alert variant="destructive" className="dashboard-error space-y-2">
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>
        <div
          ref={containerRef}
          className={`error-report-container ${expanded ? 'expanded' : ''}`}
        >
          <ul className="error-report-list">
            {errors.map((err, idx) => (
              <li key={idx} className="error-report-item">
                <div className="error-report-header">
                  <ErrorTypeBadge type={err.type} />
                  <span className="error-report-location">
                    {err.filename}:{err.lineno}
                  </span>
                  {err.count > 1 && (
                    <span className="error-report-count">x{err.count}</span>
                  )}
                </div>
                <div className="error-report-message">{err.message}</div>
                {err.source && (
                  <pre className="error-report-source"><code>{err.source}</code></pre>
                )}
              </li>
            ))}
          </ul>
        </div>
        {wasOverflowingWhenCollapsed && (
          <button
            className="error-report-toggle"
            onClick={() => setExpanded(prev => !prev)}
          >
            {expanded ? 'Show less' : 'Show all'}
          </button>
        )}
      </AlertDescription>
    </Alert>
  );
};

export { ErrorsReport as default, ErrorsReport };
