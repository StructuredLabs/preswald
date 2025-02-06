import React from 'react';

import { HoverCard, HoverCardContent, HoverCardTrigger } from '@/components/ui/hover-card';

export const Tooltip = ({ content, children }) => {
  return (
    <HoverCard>
      <HoverCardTrigger asChild>
        <div className="inline-block">{children}</div>
      </HoverCardTrigger>
      <HoverCardContent
        side="top"
        align="center"
        className="px-3 py-1.5 text-xs font-medium bg-popover text-popover-foreground"
      >
        {content}
      </HoverCardContent>
    </HoverCard>
  );
};
