import React, { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { cn } from '@/lib/utils';

const CONNECTION_TYPES = [
  { value: 'csv', label: 'CSV File' },
  { value: 'json', label: 'JSON File' },
  { value: 'parquet', label: 'Parquet File' },
  { value: 'postgres', label: 'PostgreSQL Database' },
];

const ConnectionInterfaceWidget = ({ className, onConnect, disabled = false }) => {
  const [source, setSource] = useState('');
  const [type, setType] = useState('csv');

  const handleConnect = () => {
    if (onConnect) {
      onConnect({ source, type });
    } else {
      alert(`Connecting to ${source} as ${type}`);
    }
  };

  return (
    <Card className={cn('connectioninterface-card', className)}>
      <CardHeader>
        <CardTitle>Connection Interface</CardTitle>
      </CardHeader>
      <CardContent className="connectioninterface-card-content">
        <div className="connectioninterface-input-group">
          <Label htmlFor="source">Data Source</Label>
          <Input
            id="source"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="Enter data source path or URL"
            disabled={disabled}
          />
        </div>

        <div className="connectioninterface-input-group">
          <Label htmlFor="type">Connection Type</Label>
          <Select value={type} onValueChange={setType} disabled={disabled}>
            <SelectTrigger id="type">
              <SelectValue placeholder="Select connection type" />
            </SelectTrigger>
            <SelectContent>
              {CONNECTION_TYPES.map(({ value, label }) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button
          className="connectioninterface-button"
          onClick={handleConnect}
          disabled={!source.trim() || disabled}
        >
          Connect
        </Button>
      </CardContent>
    </Card>
  );
};

export default ConnectionInterfaceWidget;
