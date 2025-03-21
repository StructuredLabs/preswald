import React, { useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const FastplotlibWidget = ({ label, src, className }) => {
    return (
        <Card className={cn('w-full p-4 flex justify-center', className)}>
            <img src={src} alt={label} className="max-w-full h-auto" />
        </Card>
    );
};

export default FastplotlibWidget;
