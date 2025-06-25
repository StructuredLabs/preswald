import { AlertTriangle, CheckCircle2, Info, XCircle } from 'lucide-react';
import React from 'react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

const levelConfig = {
  success: {
    icon: CheckCircle2,
    variant: 'success',
    title: 'Success',
  },
  warning: {
    icon: AlertTriangle,
    variant: 'warning',
    title: 'Warning',
  },
  error: {
    icon: XCircle,
    variant: 'destructive',
    title: 'Error',
  },
  info: {
    icon: Info,
    variant: 'default',
    title: 'Information',
  },
};

const AlertWidget = ({ id, message, level = 'info', className, error }) => {
  const config = levelConfig[level] || levelConfig.info;
  const Icon = config.icon;

  return (
    <div id={id} className='relative'>
      {error && (
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="absolute top-2 right-2 text-destructive z-10 pointer-events-auto cursor-pointer">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <span>{error.toString()}</span>
          </TooltipContent>
        </Tooltip>
      )}

      <Alert variant={config.variant}
             className={cn('alertwidget-container',
             className,
             error && 'border-destructive border-2 bg-red-50 rounded-md')}>
        <Icon className={cn("alertwidget-icon", error && 'text-gray-300')} />
        <AlertTitle>{config.title}</AlertTitle>
        <AlertDescription>{message}</AlertDescription>
      </Alert>
    </div>
  );
};

export default AlertWidget;
