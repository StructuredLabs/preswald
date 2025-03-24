import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';

import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { comm } from '@/utils/websocket';

const FastplotlibWidget = ({ id, label, src, className, clientId }) => {
  const [currentSrc, setCurrentSrc] = useState(src);

  useEffect(() => {
    if (clientId) {
      comm.updateComponentState("client_id", clientId);
      console.debug(`[FastplotlibWidget:${id}] has clientId ${clientId}`);
    }
  }, [clientId]);

  useEffect(() => {
    const unsubscribe = comm.subscribe((message) => {
      if (
        message.type === 'image_update' &&
        message.component_id === id &&
        message.value
      ) {
        console.debug(`[FastplotlibWidget:${id}] received new image`);
        setCurrentSrc(message.value);
      }
    });

    return () => unsubscribe();
  }, [id]);

  return (
    <Card className={cn('w-full p-4 flex justify-center', className)}>
      {!currentSrc ? (
            <div className="text-sm text-muted-foreground">No image available</div>
      ) : (
        <img src={currentSrc} alt={label || 'Fastplotlib chart'} className="max-w-full h-auto" />
      )}
    </Card>
  );
};

FastplotlibWidget.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  src: PropTypes.string.isRequired,
  className: PropTypes.string,
};

export default FastplotlibWidget;
