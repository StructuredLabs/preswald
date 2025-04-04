import React from 'react';

import { Badge } from '@/components/ui/badge';

export function PreswaldBadge() {
  return (
    <a
      href="https://preswald.com"
      target="_blank"
      rel="noopener noreferrer"
      className="fixed top-0 right-0 z-50 no-underline transition-opacity hover:opacity-90 block m-0 p-0 leading-none"
    >
      <Badge className="bg-black hover:bg-black/90 text-white rounded-none rounded-bl-md font-medium px-3 py-1.5 block m-0 leading-none inline-flex items-center tracking-tight text-[13px] shadow-sm transition-colors">
        Built with Preswald
      </Badge>
    </a>
  );
}
