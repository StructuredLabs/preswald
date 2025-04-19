import { ChevronDown } from 'lucide-react';

import React from 'react';

import { Card } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

const CollapsibleWidget = ({ _label, _open = true, children }) => {
  const [isOpen, setIsOpen] = React.useState(_open);

  return (
    <Card className="mb-4 p-4 rounded-2xl shadow-md">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div
          className="flex justify-between items-center cursor-pointer"
          onClick={() => setIsOpen(!isOpen)}
        >
          <h2 className="font-semibold text-lg">{_label}</h2>
          <ChevronDown className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </div>
        <CollapsibleContent>
          <div className="mt-4">{children}</div>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};

export default CollapsibleWidget;
