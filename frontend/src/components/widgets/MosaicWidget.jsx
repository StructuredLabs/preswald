import vegaEmbed from 'vega-embed';

import React, { useEffect, useRef } from 'react';

import { Card } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const MosaicWidget = ({ spec, className }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current && spec) {
      vegaEmbed(containerRef.current, spec) // {actions: false} to remove extra options
        .then((result) => console.log(result))
        .catch((error) => console.error(error));
    }
  }, [spec]);

  return (
    <Card className={cn('w-full overflow-x-auto', className)}>
      <div ref={containerRef}></div>;
    </Card>
  );
};

export default MosaicWidget;
