import React from 'react';

import { Card } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const MatplotlibWidget = ({ _label, image, className }) => {
  return (
    <Card className={cn('w-full', className)}>
      {_label && <h3 className="text-lg font-medium mb-2">{_label}</h3>}
      {image ? (
        <img src={`data:image/png;base64,${image}`} alt="Matplotlib Plot" className="w-full" />
      ) : (
        <p>No plot available</p>
      )}
    </Card>
  );
};

export default MatplotlibWidget;
