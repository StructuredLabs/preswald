import React, { useState, useRef, useEffect } from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';

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

  return (
    <Alert variant="destructive" className="dashboard-error space-y-2">
      <AlertTitle>Errors detected during source transformation</AlertTitle>
      <AlertDescription>
        <div
          ref={containerRef}
          className={`error-report-container ${expanded ? 'expanded' : ''}`}
        >
          <ul className="error-report-list">
            {errors.map((err, idx) => (
              <li key={idx}>
                <strong>{err.filename}:{err.lineno}</strong> - {err.message}
                {err.count > 1 ? ` (x${err.count})` : null}
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
