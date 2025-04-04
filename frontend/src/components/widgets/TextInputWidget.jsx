import React from 'react';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import { cn } from '@/lib/utils';

const TextInputWidget = ({
  label,
  placeholder,
  value = '',
  onChange,
  className,
  disabled = false,
}) => {
  return (
    <div className={cn('flex flex-col gap-2', className)}>
      {label && <Label className="text-sm font-medium">{label}</Label>}
      <Input
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full"
      />
    </div>
  );
};

export default TextInputWidget;
