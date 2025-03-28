import React, { useEffect, useRef } from 'react';

import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const FastplotlibWidget = ({ data, width, height, size, className }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = width;
    canvas.height = height;

    const byteArray = new Uint8Array(data.match(/.{1,2}/g).map((byte) => parseInt(byte, 16)));
    const blob = new Blob([byteArray], { type: 'image/png' });
    const img = new Image();

    img.onload = () => {
      ctx.drawImage(img, 0, 0, width, height);
      URL.revokeObjectURL(img.src);
    };
    img.src = URL.createObjectURL(blob);
  }, [data, width, height]);

  return (
    <Card className={cn('w-full', className)}>
      <canvas
        ref={canvasRef}
        style={{ width: `${width * size}px`, height: `${height * size}px` }}
      />
    </Card>
  );
};

export default React.memo(FastplotlibWidget);
