import React, { useEffect, useRef } from 'react';

import { Card } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const FastplotlibWidget = ({ data, width, height, size, className }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    const imgData = ctx.createImageData(width, height);

    // Convert RGB to RGBA (add alpha channel = 255)
    for (let i = 0, j = 0; i < data.length; i += 3, j += 4) {
      imgData.data[j] = data[i]; // R
      imgData.data[j + 1] = data[i + 1]; // G
      imgData.data[j + 2] = data[i + 2]; // B
      imgData.data[j + 3] = 255; // A
    }

    ctx.putImageData(imgData, 0, 0);
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
