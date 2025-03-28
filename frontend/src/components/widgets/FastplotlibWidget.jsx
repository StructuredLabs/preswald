import PropTypes from 'prop-types';

import React, { useEffect, useState } from 'react';

import { Card } from '@/components/ui/card';

import { cn } from '@/lib/utils';
import { comm } from '@/utils/websocket';

const FastplotlibWidget = ({ id, label, src, className, clientId }) => {
  const [currentSrc, setCurrentSrc] = useState(src);
  const [hasLoadedOnce, setHasLoadedOnce] = useState(!!src);
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (clientId) {
      comm.updateComponentState('client_id', clientId);
    }
  }, [clientId]);

  useEffect(() => {
    const unsubscribe = comm.subscribe((message) => {
      if (message.type === 'image_update' && message.component_id === id) {
        if (message.value) {
          setCurrentSrc(message.value);
          setHasLoadedOnce(true);
          setShowWarning(false); // reset warning on valid data
        } else {
          console.warn(`[FastplotlibWidget:${id}] image update received without data.`);
          setShowWarning(true); // show warning if data missing
        }
      }
    });

    return () => unsubscribe();
  }, [id]);

  return (
    <Card className={cn('w-full p-4 flex justify-center items-center relative', className)}>
      {hasLoadedOnce ? (
        <>
          <img src={currentSrc} alt={label || 'Fastplotlib chart'} className="max-w-full h-auto" />
          {showWarning && (
            <div className="absolute bottom-0 left-0 right-0 bg-yellow-100 text-yellow-800 text-xs p-1 text-center">
              Warning: Latest update did not include data.
            </div>
          )}
        </>
      ) : (
        <div className="text-sm text-muted-foreground">Loading...</div>
      )}
    </Card>
  );
};

FastplotlibWidget.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  src: PropTypes.string,
  className: PropTypes.string,
  clientId: PropTypes.string,
};

export default React.memo(FastplotlibWidget);
