import { Check, Copy, AlertTriangle } from 'lucide-react';
import React, { useState } from 'react';
import { JSONTree } from 'react-json-tree';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';

import { cn } from '@/lib/utils';

const JSONViewerWidget = ({
  id,
  data,
  title,
  expanded = true,
  className,
  error,
}) => {
  const [copied, setCopied] = useState(false);

  const theme = {
    scheme: 'default',
    base00: '#ffffff',
    base01: '#f5f5f5',
    base02: '#dcdcdc',
    base03: '#c0c0c0',
    base04: '#808080',
    base05: '#404040',
    base06: '#202020',
    base07: '#000000',
    base08: '#aa3731',
    base09: '#d88513',
    base0A: '#c99e00',
    base0B: '#448c27',
    base0C: '#008fa1',
    base0D: '#006bb3',
    base0E: '#a64ef1',
    base0F: '#d33000',
  };

  const handleCopy = () => {
    try {
      const jsonString = JSON.stringify(data, null, 2);
      navigator.clipboard.writeText(jsonString);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (err) {
      console.error('Failed to copy JSON:', err);
    }
  };

  return (
    <Card
      id={id}
      className={cn(
        'relative overflow-auto text-sm',
        error && 'border-destructive border-2 bg-red-50 rounded-md',
        className
      )}
    >
      {error && (
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="absolute top-2 right-2 text-destructive z-10">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <span>{error.toString()}</span>
          </TooltipContent>
        </Tooltip>
      )}
      <CardContent>
        <div className="flex justify-between items-center mb-2">
          {title && <h3 className="font-semibold">{title}</h3>}
          <Button
            variant={copied ? 'success' : 'outline'}
            size="sm"
            onClick={handleCopy}
            className={cn(
              'gap-1 text-muted-foreground transition-all duration-200',
              copied && 'text-green-600 border-green-500 bg-green-50'
            )}
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy JSON
              </>
            )}
          </Button>
        </div>
        {error ? (
          <div className="text-destructive italic">Unable to display JSON.</div>
        ) : (
          <JSONTree
            data={data}
            theme={theme}
            invertTheme={false}
            shouldExpandNodeInitially={() => expanded}
            hideRoot={true}
          />
        )}
      </CardContent>
    </Card>
  );
};

export default JSONViewerWidget;
