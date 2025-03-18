import { AlertTriangle, CheckCircle2, Info, XCircle } from 'lucide-react';

import React from 'react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

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

const AlertWidget = ({ message, level = 'info', className }) => {
  const config = levelConfig[level] || levelConfig.info;
  const Icon = config.icon;

  return (
    <Alert variant={config.variant} className={cn('alertwidget-container', className)}>
      <Icon className="alertwidget-icon" />
      <AlertTitle>{config.title}</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
};

export default AlertWidget;
