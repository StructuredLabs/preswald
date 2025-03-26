import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { comm } from '@/utils/websocket';

/**
 * FastplotlibWidget renders images streamed from the backend via WebSocket.
 *
 * @param {string} id - Unique identifier of the component instance.
 * @param {string} label - Accessible label describing the chart/image.
 * @param {string} src - Initial image URL or base64 source.
 * @param {string} className - Additional CSS classes.
 * @param {string} clientId - ID used to communicate with the backend.
 */
const FastplotlibWidget = ({ id, label, src, className, clientId }) => {
  const [currentSrc, setCurrentSrc] = useState(src);
  const [isLoading, setIsLoading] = useState(!src);

  useEffect(() => {
    if (clientId) {
      comm.updateComponentState('client_id', clientId);
    }
  }, [clientId]);

  useEffect(() => {
    const unsubscribe = comm.subscribe((message) => {
      if (
        message.type === 'image_update' &&
        message.component_id === id &&
        message.value
      ) {
        setCurrentSrc(message.value);  // base64 URL, safe to directly set
        setIsLoading(false);
      }
    });

    return () => unsubscribe();
  }, [id]);

  return (
    <Card className={cn('w-full p-4 flex justify-center items-center', className)}>
      {isLoading ? (
        <div className="text-sm text-muted-foreground">Loading...</div>
      ) : currentSrc ? (
        <img
          src={currentSrc}
          alt={label || 'Fastplotlib chart'}
          className="max-w-full h-auto"
        />
      ) : (
        <div className="text-sm text-muted-foreground">No image available</div>
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
