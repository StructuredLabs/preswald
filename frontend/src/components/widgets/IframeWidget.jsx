import React from 'react';

import { Card } from '@/components/ui/card';
import { Iframe } from '@/components/ui/iframe';

export default function IframeWidget({ url, height, width, title }) {
  return (
    <Card className="mb-4 p-2 overflow-hidden flex justify-center">
      <Iframe url={url} height={height} width={width} title={title} />
    </Card>
  );
}
