import PropTypes from 'prop-types';
import { useEffect, useRef } from 'react';

import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { comm } from '@/utils/websocket';

const FastplotlibWidget = ({ id, label, data, width, height, size, className, clientId }) => {
  const canvasRef = useRef(null);

  // register client_id with backend state
  useEffect(() => {
    if (clientId) {
      comm.updateComponentState('client_id', clientId);
      console.debug(`[FastplotlibWidget:${id}] has clientId ${clientId}`);
    }
  }, [clientId]);

  // subscribe to image updates over WebSocket
  useEffect(() => {
    const unsubscribe = comm.subscribe((message) => {
      if (
        message.type === 'image_update' &&
        message.component_id === id &&
        message.value
      ) {
        console.debug(`[FastplotlibWidget:${id}] received new image`);
        renderImage(message.value);
      }
    });

    return () => unsubscribe();
  }, [id]);

  // render image into canvas
  const renderImage = (hexData) => {
    const canvas = canvasRef.current;
    if (!canvas || !hexData) return;

    const ctx = canvas.getContext('2d');
    canvas.width = width;
    canvas.height = height;

    const byteArray = new Uint8Array(hexData.match(/.{1,2}/g).map((byte) => parseInt(byte, 16)));
    const blob = new Blob([byteArray], { type: 'image/png' });
    const img = new Image();

    img.onload = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
      URL.revokeObjectURL(img.src);
    };
    img.src = URL.createObjectURL(blob);
  };

  useEffect(() => {
    if (data) renderImage(data);
  }, [data]);

  return (
    <Card className={cn('w-full p-4 flex justify-center', className)}>
      <canvas
        ref={canvasRef}
        style={{ width: `${width * size}px`, height: `${height * size}px` }}
      />
    </Card>
  );
};

FastplotlibWidget.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  data: PropTypes.string,
  width: PropTypes.number.isRequired,
  height: PropTypes.number.isRequired,
  size: PropTypes.number,
  className: PropTypes.string,
  clientId: PropTypes.string,
};

export default React.memo(FastplotlibWidget);
